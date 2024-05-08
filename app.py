#!/usr/bin/env python

# ============================================================================================
# app.py
# Authors: Edouard Kwizera, Roshaan Khalid, Jourdain Babisa, Wangari Karani
# ============================================================================================

# Standard library imports
from datetime import datetime
from gevent import monkey
monkey.patch_all()
import uuid
import io
import os

# Related third-party imports
import flask
from flask import (
    jsonify, request, flash, redirect,
    session, url_for, render_template, send_file
    )
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from sqlalchemy.orm import joinedload
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, emit
from reportlab.lib.pagesizes import letter
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

# Local application/library specific imports
import db_operations
from req_lib import ReqLib
from auth import authenticate
from conciseNotes import LectureNoteSummarizer
from database import (
    ChatMessage, ClassSession, Question,
    SessionLocal, User, Student, Class, Enrollment, Answer
)

load_dotenv()
app = flask.Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "123456")
socketio = SocketIO(app, cors_allowed_origins="*")
csrf = CSRFProtect(app)

database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
        "postgres://", "postgresql://"
    )
else:
    print("The DATABASE_URL environment variable is not set.")

# ============================================================================================
# Getting Started
# ============================================================================================

@app.route("/", methods=["GET"])
def index():
    """
    The root endpoint that determines the initial direction for the user based on their session status.
    If the user has a 'visited' flag in their session, it suggests they've interacted with the site before
    and are redirected to authentication. If not, they are directed to start the initial setup or onboarding
    process.
    """
    if 'visited' in session:
        return redirect(url_for("authenticate_and_direct"))
    return redirect(url_for("get_started"))




@app.route("/get-started", methods=["GET"])
def get_started():
    """
    Initiates user onboarding by authenticating the user and then directing them
    to a role selection or a general home page if already authenticated or no
    specific role selection is needed.
    """
    # Authenticate the user
    username = authenticate()

    # Check if authentication was successful
    if username:
        # Store the username in the session to maintain user state
        flask.session['username'] = username

        # Check if the user has already selected a role, if not direct to role selection
        if 'role' not in flask.session:
            return flask.redirect(url_for("role_selection"))

        # If the role is already set, redirect to the home page
        return flask.redirect(url_for("home"))

    # If authentication fails, render the home template which might prompt login or show error
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response



@app.route("/home", methods=["GET"])
def home():
    """
    Directs users to their respective dashboards based on their roles (student or professor).
    If the role is not defined in the session, it defaults to displaying the general home page.
    This ensures that users receive a personalized experience based on their role.
    """
    # Check if the role is defined in the session
    if 'role' in session:
        role = flask.session['role']

        # Direct student users to the student dashboard
        if role == 'student':
            return redirect(url_for("student_dashboard"))

        # Direct professor users to their specific class dashboard
        elif role == 'professor':
            username = flask.session['username']
            # Retrieve the class ID associated with the professor
            class_id = db_operations.get_professors_class_id(username)
            # If a class ID is found, redirect to the professor dashboard for that class
            if class_id:
                return redirect(url_for("professor_dashboard", class_id=class_id))
            # If no class ID is found, consider redirecting to a page that handles this case or back to home
            else:
                flash("No class associated with the professor. Please contact support.", "error")
                return redirect(url_for("home"))

    # Render and return the general home page if no specific role actions are required
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response


@app.route("/logout", methods=["GET"])
def logout():
    """
    Processes the user's logout request. Before clearing the session, it checks if the user
    (assumed to be an instructor) has any active class sessions. If an active session exists,
    the logout is prevented, and an error message is returned. Otherwise, the user's session
    is cleared, and a successful logout message is returned.
    """
    # Initialize a database session
    db = SessionLocal()
    try:
        # Retrieve the user ID from the session
        user_id = flask.session.get("username")
        
        # Check if the user is an instructor with an active class session
        if user_id:
            active_session = (
                db.query(ClassSession)
                .join(Class, ClassSession.class_id == Class.class_id)
                .filter(Class.instructor_id == user_id, ClassSession.is_active == True)
                .first()
            )
            if active_session:
                # Prevent logout and return a message if there is an active session
                return jsonify({
                    "success": False,
                    "message": "There is an active session. Please end the session before logging out."
                }), 400

        # Clear the user's session to log them out
        flask.session.clear()

        # Return a success message upon logout
        return jsonify({"success": True, "message": "You have been logged out successfully."})

    except Exception as e:
        # Return an error message if an exception occurs
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure the database session is closed regardless of the outcome
        db.close()


@app.route("/role-selection")
def role_selection():
    """
    Displays a role selection page to the user. This route renders an HTML template that allows users
    to choose their role within the application (e.g., student, professor, administrator).
    """
    # Render the role selection HTML template
    html_code = flask.render_template("role-selection.html")
    
    # Create a response object from the rendered HTML code
    response = flask.make_response(html_code)
    
    # Return the response object to the client
    return response

@app.route("/select_role", methods=["POST"])
def select_role():
    """
    Handles the selection of a user's role via a POST request. The selected role is stored
    in the session, and the route responds with a JSON object indicating success and providing
    a URL for redirection to an authentication and direction route.
    """
    # Retrieve the role from the JSON body of the POST request
    role = request.json["role"]

    # Store the selected role in the user's session
    flask.session["role"] = role

    # Return a JSON response with success status and a redirection URL
    return jsonify({
        "success": True, 
        "redirectUrl": url_for("authenticate_and_direct")
    })



@app.route("/authenticate_and_direct", methods=["GET"])
def authenticate_and_direct():
    """
    Authenticates the user, verifies their role, and directs them to the appropriate dashboard.
    It handles session management and ensures that users are redirected based on their role
    and whether they are associated with a class. It also handles role mismatches and
    creates new user entries if necessary.
    """
    # Authenticate user and store username in session
    username = authenticate()
    flask.session["username"] = username
    
    # Retrieve and verify user role
    actual_role = db_operations.get_user_role(username)
    if actual_role:
        flask.session["actual_role"] = actual_role
        if actual_role != flask.session.get("role"):
            flash(f"Access denied. Your role is {actual_role}.", "error")
            return flask.redirect(flask.url_for("get_started"))

        flask.session['visited'] = True
        
        # Redirect professor to their dashboard or class creation form
        if actual_role == "professor":
            class_id = db_operations.get_professors_class_id(username)
            if not class_id:
                print(f"No class associated with the professor {username}")
                return flask.redirect(flask.url_for("create_class_form"))
            flask.session['class_id'] = class_id  
            return flask.redirect(flask.url_for("professor_dashboard", class_id=class_id))
        
        # Redirect student to their dashboard
        elif actual_role == "student":
            class_id = db_operations.get_students_class_id(username)
            if not class_id:
                return flask.redirect(url_for("student_dashboard"))
            flask.session['class_id'] = class_id 
            return flask.redirect(flask.url_for("student_dashboard", class_id=class_id))
    else:
        # Default to student role if not found, create user, and redirect accordingly
        role = flask.session.get("role", "student")
        db_operations.create_user(username, role)
        flask.session['visited'] = True
        if role == "professor":
            class_id = db_operations.get_professors_class_id(username)
            if not class_id:
                return flask.redirect(flask.url_for("create_class_form"))
            flask.session['class_id'] = class_id  
            return flask.redirect(flask.url_for("professor_dashboard", class_id=class_id))
        else:
            dashboard_url = "student_dashboard"
            return flask.redirect(flask.url_for(dashboard_url))
        
@app.route('/get-current-user')
def get_current_user():
    """
    Retrieves the currently logged-in user's ID from the session. If a user is logged in,
    their user ID is returned. If no user is logged in, it returns an error message.
    """
    # Attempt to retrieve the user ID from the session
    user_id = session.get('username', None)
    
    # Debug print statement to check the user ID retrieval
    print(f"user_id: {user_id}")

    # Check if a user ID was retrieved
    if user_id:
        # If a user ID exists, return it with a success status
        return jsonify({'success': True, 'userId': user_id})
    else:
        # If no user ID exists, return an error message and a 404 status
        return jsonify({'success': False, 'message': 'No user logged in'}), 404

    
    
# -------------------------------------------------------------------------------------------- #
# Search Classes
# -------------------------------------------------------------------------------------------- #
@app.route("/search_classes", methods=["GET"])
def search_classes():
    """
    Allows users to search for classes by title. This route checks for user authentication,
    validates the presence of a search term, and returns a list of classes that match the
    search criteria along with their instructors.
    """
    # Ensure the user is authenticated by checking for 'username' in the session
    if "username" not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401

    # Initialize database session
    db = SessionLocal()
    try:
        # Retrieve the search term from the query parameters and convert it to lower case
        search_term = request.args.get("search", "").lower()
        if not search_term:
            # Return an error if no search term is provided
            return jsonify({"success": False, "message": "Search term is required"}), 400
        
        # Perform a query to find classes whose titles contain the search term, joining with the User table
        # to get instructor information
        classes = (
            db.query(Class)
            .join(Class.instructor)
            .filter(Class.title.ilike(f"%{search_term}%"))
            .options(joinedload(Class.instructor))
            .all()
        )

        # Transform the resulting classes into a list of dictionaries for JSON serialization
        classes_data = [
            {
                "id": cls.class_id,
                "name": cls.title,
                "instructor": cls.instructor.name,
            }
            for cls in classes
        ]

        # Return a successful response with the list of matching classes
        return jsonify({"success": True, "classes": classes_data})
    finally:
        # Close the database session to free resources
        db.close()


# ============================================================================================ #
# Professor Dashboard
# ============================================================================================ #

@app.route("/professor_dashboard/<class_id>")
def professor_dashboard(class_id):
    """
    Displays the professor's dashboard for a specific class. This route checks for user authentication,
    retrieves the user's display name from an external configuration, fetches the name of the class,
    and then renders a dashboard view with this information.
    """
    # Check if the user is logged in by verifying the presence of a username in the session
    username = flask.session.get("username")
    if not username:
        # Redirect to the home page if the user is not authenticated
        return flask.redirect(url_for("home"))
    
    # Instance of ReqLib to handle external requests
    req_lib = ReqLib()

    # Retrieve the display name for the user using an external service
    display_name_data = req_lib.getJSON(req_lib.configs.USERS, uid=username)
    # Extract the display name from the returned data
    display_name = display_name_data[0].get('displayname') if display_name_data and len(display_name_data) > 0 else "Professor"

    # Fetch the name of the class the professor is teaching
    course_name = db_operations.get_professor_class(username)

    # Render and return the dashboard template, passing necessary data for display
    return flask.render_template(
        "professor-dashboard.html",
        course_name=course_name,
        username=display_name,
        class_id=class_id,
        user_id=username  # Pass the user ID for potential further use in the template
    )


# -------------------------------------------------------------------------------------------- #
# Professor : Create class 
# -------------------------------------------------------------------------------------------- #

@app.route("/create_class_form", methods=["GET"])
def create_class_form():
    """
    Displays the form for creating a new class. This route handles the GET request
    to show the 'create_class_form.html' template, where professors can input the
    necessary information to create a class.
    """
    # Render and return the HTML form template for creating a new class
    return flask.render_template("create_class_form.html")




@app.route("/create_class", methods=["POST"])
def create_class():
    """
    Creates a new class for a professor. The professor's username is retrieved from the session,
    and the class name is taken from the submitted form data. This route handles the POST request
    to create a new class and returns a JSON response indicating the success or failure of the operation.
    """
    # Retrieve the class name from the form data
    class_name = request.form.get("class_name")
    
    # Get the username from the session, which represents the logged-in user (professor)
    username = flask.session.get("username")

    # Call the database operation to create a new class associated with the professor
    success, class_id_returned = db_operations.create_class_for_professor(
        username, class_name
    )

    # Check if the class creation was successful
    if success:
        # Return a JSON response with success status, message, and the new class ID
        return jsonify({
            'status': 'success',
            'message': 'Class successfully created!',
            'class_id': class_id_returned
        })
    else:
        # Return a JSON response with error status and message if creation failed
        return jsonify({
            'status': 'error',
            'message': 'Error creating class.'
        }), 400


# -------------------------------------------------------------------------------------------- #
# Professor : Manage members of the class
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/userlist")
def class_userlist(class_id):
    """
    Retrieves and displays a list of students enrolled in a specific class. This route uses a template
    to render the user list, and handles exceptions to provide a robust user experience even in cases
    of operational failures.
    """
    try:
        # Retrieve data for all students in the specified class
        users_data = db_operations.get_students_for_class(class_id)
        
        # Render a template to display the list of users, passing the retrieved data and class ID
        return render_template("class-users.html", users=users_data, class_id=class_id)
    except Exception as e:
        # Log the exception for debugging purposes
        print(e)
        
        # Return a JSON response with an error message and a 500 Internal Server Error status
        return (
            jsonify({"success": False, "message": "Unable to fetch class users"}),
            500,
        )


@app.route("/edit_student/<class_id>/<user_id>", methods=["GET", "POST"])
def edit_user(class_id, user_id):
    """
    Edits the details of a student in a specific class. Handles both GET requests to display the form
    with the student's current details and POST requests to update those details.
    """
    # Initialize a database session
    db_session = SessionLocal()
    
    try:
        # Fetch the student by user ID
        student = db_session.query(Student).filter_by(user_id=user_id).first()

        if student is None:
            flash("Student not found.", "error")
            return redirect(url_for("class_userlist", class_id=class_id))

        # Fetch enrollment details for the student
        enrollment = db_session.query(Enrollment).filter_by(student_id=user_id).first()
        
        if request.method == "POST":
            if enrollment:
                # Update the student's score and TA status if provided in the form
                enrollment.score = request.form.get("score", enrollment.score)
                enrollment.is_ta = bool(int(request.form.get("is_ta", enrollment.is_ta)))
                db_session.commit()
                flash("Student information updated successfully.", "success")
            else:
                flash("Enrollment information not found.", "error")
            return redirect(url_for("professor_dashboard", class_id=class_id))
        else:
            # If GET method, render the edit student template with current details
            return render_template("edit_student.html", student=student,
                                   class_id=class_id, score=enrollment.score
                                   if enrollment else None, is_ta=enrollment.is_ta
                                   if enrollment else None)
    except Exception as e:
        # Handle exceptions and rollback any failed transactions
        db_session.rollback()
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("class_userlist", class_id=class_id))
    finally:
        # Ensure the database session is closed
        db_session.close()

    

@app.route("/delete_user/<class_id>/<user_id>", methods=["POST"])
def delete_user(class_id, user_id):
    """
    Deletes a user (student) from a specific class. This route handles the deletion of the user's enrollment record.
    If the user exists, their enrollment in the specified class is deleted. If the user is not found, or there is no
    enrollment, appropriate feedback is provided.
    """
    # Initialize a database session
    db_session = SessionLocal()

    try:
        # Fetch the user to check if they exist
        user = db_session.query(User).filter_by(user_id=user_id).first()

        if user:
            # Query to find the user's enrollment in the specified class
            delete_enrollment = db_session.query(Enrollment).filter(Enrollment.student_id == user_id, Enrollment.class_id == class_id).first()
            
            # Check if the enrollment record exists
            if delete_enrollment:
                # Delete the enrollment record if it exists
                db_session.delete(delete_enrollment)
                db_session.commit()
                flash("User successfully deleted", "success")
            else:
                # If no enrollment is found, flash an error message
                flash("Enrollment record not found.", "error")
        else:
            # If the user is not found, flash an error message
            flash("User not found.", "error")
    except Exception as e:
        # Rollback in case of any exception during the database operation
        db_session.rollback()
        flash(f"Error deleting user: {str(e)}", "error")
    finally:
        # Close the database session to free resources
        db_session.close()

    # Redirect to the professor dashboard for the class
    return redirect(url_for("professor_dashboard", class_id=class_id))


# -------------------------------------------------------------------------------------------- #
# Professor : Manage In-Class Questions
# -------------------------------------------------------------------------------------------- #

@app.route("/add-question")
def add_question():
    """this method will render a form with input to add questions

    Returns:
        _type_: render template
    """
    return flask.render_template("add-question.html")


@app.route("/class/<class_id>/add-question", methods=["POST"])
def add_question_to_class_route(class_id):
    """
    Adds a new question to a class based on the provided class_id. This endpoint
    checks if the required fields (question text and correct answer) are provided and
    validates that their lengths do not exceed a set maximum before attempting to add the question.
    """
    # Extract question details from request JSON
    data = request.json
    question_text = data.get("question_text")
    correct_answer = data.get("correct_answer")

    # Ensure both question text and correct answer are provided
    if not question_text or not correct_answer:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Missing question text or correct answer.",
                }
            ),
            400,
        )
    
    # Set the maximum acceptable length for question text and correct answer
    max_length = 200
    # Validate the length of the question text and correct answer
    if len(question_text) > max_length or len(correct_answer) > max_length:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Question text or correct answer exceeds maximum length of 200 characters.",
                }
            ),
            400,
        )
    
    # Attempt to add the question to the class in the database
    success = db_operations.add_question_to_class(
        class_id, question_text, correct_answer
    )

    # Check if the database operation was successful
    if success:
        return jsonify({"success": True, "message": "Question successfully added."})
    else:
        # Return an error if the operation fails
        return jsonify({"success": False, "message": "Failed to add question."}), 500

    

@app.route("/class/<string:class_id>/question/<string:question_id>/edit", methods=["POST"])
def edit_question(class_id, question_id):
    """
    Modifies the details of a specific question in a class, provided the question is not currently
    active, displayed, or has associated summaries. Validates the length of the question and answer
    text to ensure it does not exceed the maximum allowed length.
    """
    # Retrieve the new question data from the request's JSON body
    data = request.get_json()
    print(data)  # Log data for debugging purposes

    # Initialize a database session
    db = SessionLocal()
    try:
        # Query for the specific question using question_id and class_id
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )

        # Check if the question exists
        if question:
            # Check if the question has restrictions that prevent editing
            if question.summaries or question.is_displayed or question.is_active:
                messages = []
                if question.summaries:
                    messages.append("This question has summaries associated with it.")
                if question.is_displayed:
                    messages.append("This question is currently displayed to students.")
                if question.is_active:
                    messages.append("This question is currently active.")
                
                return jsonify({
                    "success": False,
                    "message": " ".join(messages)
                }), 403

            # Validate the length of the updated question and answer
            max_question_length = 200
            max_answer_length = 200
            if len(data["question_text"]) > max_question_length or len(data["correct_answer"]) > max_answer_length:
                messages = ["One or both fields exceeds maximum length of 200 characters. Please try again."]
                return jsonify({"success": False, "message": " ".join(messages)}), 403

            # Update question text and correct answer if validations pass
            question.text = data["question_text"]
            question.correct_answer = data["correct_answer"]
            db.commit()  # Commit the updates to the database
            return jsonify({"success": True, "message": "Question updated successfully."})
        else:
            # Return an error if the question is not found
            return jsonify({"success": False, "message": "Question not found."}), 404
    finally:
        # Ensure that the database session is closed
        db.close()



@app.route("/class/<string:class_id>/question/<string:question_id>/delete", methods=["DELETE"])
def delete_question(class_id, question_id):
    """
    Deletes a specific question from a class, but only if the question is neither active nor displayed.
    The route checks if the question exists, verifies its state, and deletes it if conditions are met.
    Returns success or error messages based on the outcome of the delete operation.
    """
    # Initialize a database session
    db = SessionLocal()
    try:
        # Query for the specific question using question_id and class_id
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        
        # Check if the question exists
        if question:
            # Ensure the question is neither active nor displayed before deletion
            if question.is_active or question.is_displayed:
                message = "Question is "
                if question.is_active:
                    message += "active"
                if question.is_displayed:
                    if question.is_active:
                        message += " and displayed"
                    else:
                        message += "displayed"
                message += ". Please deactivate and ensure it is not displayed before deleting."
                return jsonify({"success": False, "message": message}), 400
            
            # Delete the question from the database
            db.delete(question)
            db.commit()
            return jsonify({"success": True, "message": "Question deleted successfully."})
        else:
            # Return an error if the question is not found
            return jsonify({"success": False, "message": "Question not found."}), 404
    except Exception as e:
        # Rollback in case of any exception during database operations
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database session is closed
        db.close()


# -------------------------------------------------------------------------------------------- #
# Professor : Generate Class Notes from In-Class Recording
# -------------------------------------------------------------------------------------------- #

@app.route('/process_transcript', methods=['POST'])
@csrf.exempt
def process_transcript():
    data = request.get_json()
    transcript = data.get('transcript')
    if not transcript:
        return jsonify({'error': 'No transcript provided'}), 400

    summarizer = LectureNoteSummarizer()
    notes = summarizer.create_concise_notes(transcript)
    if not notes:
        return jsonify({'error': 'Failed to generate notes'}), 500

    
    pdf_buffer = io.BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter

    textobject = p.beginText(72, height = 100)  
    textobject.setFont("Helvetica", 12)  
    lines = notes.split('\n')  
    for line in lines:
        textobject.textLine(line)  
    p.drawText(textobject)  
    p.showPage()
    p.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        mimetype='application/pdf',
        download_name='notes.pdf'
    )

# ============================================================================================ #
# Student Dashboard
# ============================================================================================ #

@app.route("/student_dashboard")
def student_dashboard():
    username = flask.session.get("username")
    if not username:
        return flask.redirect(url_for("home"))
    
    req_lib = ReqLib()
    username = req_lib.getJSON(
        req_lib.configs.USERS,
        uid=username,
    )

    username = username[0].get('displayname')
    return flask.render_template("student-dashboard.html", student_name=username)


@app.route("/enroll_in_class", methods=["POST"])
def enroll_in_class():
    """
    Enrolls a logged-in user into a specified class based on the class ID provided.
    This endpoint checks user authentication, validates the existence of the class,
    and handles duplicate enrollments, ensuring each user can enroll in a class only once.
    """
    # Retrieve username from the session to identify the logged-in user
    username = session.get("username")
    # Retrieve class ID from the JSON payload of the request
    class_id = request.json.get("class_id")

    # Validate the presence of both username and class ID
    if not username and class_id:
        # Return an error if the user is not authenticated or class ID is missing
        return jsonify({"success": False, "message": "User not authenticated"}), 401

    # Initialize database session
    db = SessionLocal()
    try:
        # Fetch user from the database
        user = db.query(User).filter_by(user_id=username).first()
        if not user:
            # Return an error if no user is found with the provided username
            return jsonify({"success": False, "message": "User not found"}), 404

        user_id = user.user_id

        # Check for existing enrollment to prevent duplicates
        existing_enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user_id, class_id=class_id)
            .first()
        )
        if existing_enrollment:
            # Return an error if the user is already enrolled in the class
            return jsonify({"success": False, "message": "Already enrolled"}), 400

        # Create new enrollment record
        enrollment = Enrollment(
            enrollment_id=str(uuid.uuid4()), student_id=user_id, class_id=class_id
        )
        db.add(enrollment)
        db.commit()
        # Return success message upon successful enrollment
        return jsonify({"success": True, "message": "Enrolled successfully"})
    except NoResultFound:
        # Handle case where no class is found with the provided ID
        return jsonify({"success": False, "message": "Class not found"}), 404
    except Exception as e:
        # Rollback the transaction in case of any exception
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database session is closed
        db.close()



@app.route("/unenroll_from_class", methods=["POST"])
def unenroll_from_class():
    """
    Handles the unenrollment of the currently logged-in student from a specified class.
    Requires user authentication and a class ID to proceed with the unenrollment.
    Returns success or error messages based on the outcome of the unenrollment process.
    """
    # Retrieve user ID from session to identify the logged-in user
    user_id = flask.session.get("username")
    
    # Check if the user is authenticated by verifying the presence of a user ID in the session
    if not user_id:
        # Return an error if the user is not authenticated
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    # Extract class ID from the request data
    data = request.get_json()
    class_id = data.get("class_id")
    
    # Check if the class ID was provided
    if not class_id:
        # Return an error if class ID is missing
        return jsonify({"success": False, "message": "Class ID is required"}), 400
    
    # Initialize database session
    db = SessionLocal()
    try:
        # Query for the specific enrollment record
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user_id, class_id=class_id)
            .first()
        )
        
        # Check if the enrollment record exists
        if not enrollment:
            # Return an error if the enrollment record is not found
            return jsonify({"success": False, "message": "Enrollment not found"}), 404
        
        # Delete the enrollment record from the database
        db.delete(enrollment)
        db.commit()
        
        # Return success message upon successful unenrollment
        return jsonify({"success": True, "message": "Unenrolled successfully"})
    except Exception as e:
        # Rollback in case of any exception during database operations
        db.rollback()
        return (
            jsonify({"success": False, "message": "Unenrollment failed: " + str(e)}),
            500,
        )
    finally:
        # Ensure that the database session is closed
        db.close()



@app.route("/get_enrolled_classes")
def get_enrolled_classes():
    """
    Retrieves a list of classes that the currently logged-in student is enrolled in.
    This endpoint requires that the user is authenticated and will respond with the
    appropriate class data or error messages depending on the user's enrollment status.
    """
    # Retrieve username from session to identify the logged-in user
    username = flask.session.get("username")
    
    # Check if the user is authenticated by verifying the presence of a username in the session
    if not username:
        # Return an error if the user is not authenticated
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    # Fetch data for classes in which the user is enrolled
    classes_data = db_operations.get_student_classes(username)
    if not classes_data:
        # Log and return an error if no classes are found for the user
        print("No classes found for user:", username)
        return (
            jsonify({"success": False, "message": "No classes found for this user."}),
            404,
        )
    
    # Return the list of classes in JSON format if classes are found
    return jsonify({"success": True, "classes": classes_data})



@app.route("/class/<class_id>/check_in", methods=["POST"])
def check_in(class_id):
    """
    Handles the POST request to check in a student for an active class session. Verifies user authentication,
    checks if the student is enrolled in the class, verifies if there is an active session, and records the
    student's attendance. It also handles already checked-in cases and errors accordingly.
    """
    # Retrieve username from session
    username = flask.session.get("username")
    
    # Check if the user is authenticated
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    
    # Verify if the user is enrolled in the class
    if not db_operations.is_student_enrolled_in_class(username, class_id):
        return jsonify({"success": False, "message": "Student not enrolled in this class"}), 403
    
    # Check for an active session in the class
    active_session = db_operations.get_active_session_for_class(class_id)
    if not active_session:
        return jsonify({"success": False, "message": "No active session for this class"}), 404
    
    # Check if the user has already checked in
    if db_operations.has_checked_in(username, active_session.session_id):
        return jsonify({
            "success": True,
            "message": "Already checked in.",
            "redirectUrl": url_for("class_dashboard", class_id=class_id),
        })

    # Record attendance and update the database
    success, message = db_operations.record_attendance_and_update(
        username, class_id, active_session.session_id
    )
    if success:
        return jsonify({
            "success": True,
            "message": "Check-in successful.",
            "redirectUrl": url_for("class_dashboard", class_id=class_id),
        })
    else:
        return jsonify({"success": False, "message": message}), 500

    

# ============================================================================================ #
# Class Dashboard
# ============================================================================================ #

@app.route("/class_dashboard/<class_id>")
def class_dashboard(class_id):
    with SessionLocal() as session:
        class_info = session.query(Class).filter(Class.class_id == class_id).first()
        if class_info:
            class_name = class_info.title
        else:
            class_name = "Class not found"
    return render_template("class-dashboard.html", class_name=class_name)


# -------------------------------------------------------------------------------------------- #
# Professor starts class session
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/start_session", methods=["POST"])
def start_class_session(class_id):
    db = SessionLocal()
    try:
        active_session = db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        if active_session:
            return jsonify({"success": False, "message": "Session already active"}), 400

        class_ = db.query(Class).filter_by(class_id=class_id).first()
        if not class_:
            return jsonify({"success": False, "message": "Class not found"}), 404
        class_.total_sessions_planned += 1
        class_.possible_scores += 1

        new_session = ClassSession(
            session_id=str(uuid.uuid4()),
            class_id=class_id,
            start_time=datetime.now(),
            is_active=True,
        )

        db.add(new_session)
        db.commit()

        session['class_session_id'] = new_session.session_id 

        return jsonify({"success": True, "message": "Class session started successfully.", "session_id": new_session.session_id}), 200

    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": "Error: " + str(e)}), 500
    finally:
        db.close()

# -------------------------------------------------------------------------------------------- #
# Professor ends class session
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/end_session", methods=["POST"])
def end_class_session(class_id):
    db = SessionLocal()
    try:
        # Fetch the active session that needs to be ended
        active_session = db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        if not active_session:
            return jsonify({
                "success": False,
                "message": "No active session found for this class"
            }), 404

        # Check for active or displayed questions
        active_or_displayed_questions = db.query(Question).filter(
            Question.class_id == class_id, (Question.is_active == True) | (Question.is_displayed == True)
        ).first()
        if active_or_displayed_questions:
            return jsonify({
                "success": False,
                "message": "There are still active or displayed questions. Please resolve them before ending the session."
            }), 400

        active_session.is_active = False
        active_session.ended = True  
        active_session.end_time = datetime.now()
        db.commit()

        return jsonify({
            "success": True,
            "message": "Class session ended successfully."
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()


# -------------------------------------------------------------------------------------------- #
# Check Class Session Status
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/session_status", methods=["GET"])
def check_class_session_status(class_id):
    with SessionLocal() as session:
        active_session = (
            session.query(ClassSession)
            .filter_by(class_id=class_id, is_active=True)
            .first()
        )
        return jsonify({"isActive": active_session is not None})
    

# ============================================================================================ #
# Feature: In-Class Questions for Student Engagement
# ============================================================================================ #

@app.route("/questions")
def questions():
    html_code = flask.render_template("Question.html")
    response = flask.make_response(html_code)
    return response


@app.route("/class/<class_id>/questions", methods=["GET"])
def get_questions_for_class_route(class_id):
    """
    Retrieves all questions associated with a specific class. Returns the questions in a JSON format
    if found, or a JSON message indicating that no questions were found if the list is empty.
    """
    # Perform a database operation to fetch questions for the specified class
    results = db_operations.get_questions_for_class(class_id)
    
    # Check if any questions were returned from the database
    if results:
        # If questions are found, return them with a success status
        return jsonify({"success": True, "questions": results})
    else:
        # If no questions are found, return a JSON response indicating failure and a 404 status
        return (
            jsonify(
                {"success": False, "message": "No questions found for this class."}
            ),
            404,
        )


# -------------------------------------------------------------------------------------------- #
# Question Status
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/question/<question_id>/status", methods=["GET"])
def get_question_status(class_id, question_id):
    """
    Retrieves the status of a specific question within a class. It checks if the question is currently
    active and whether it is displayed, returning this information in a JSON response.
    """
    # Initialize a database session
    db_session = SessionLocal()
    
    try:
        # Query the database for the specific question by class and question IDs
        question = db_session.query(Question).filter_by(
            class_id=class_id, question_id=question_id).first()
        
        # Check if the question exists
        if not question:
            # Return an error message if the question is not found
            return jsonify({"success": False, "message": "Question not found."}), 404

        # Return the status of the question including its active and displayed states
        return jsonify({
            "success": True,
            "isActive": question.is_active,
            "isDisplayed": question.is_displayed
        }), 200
    except Exception as e:
        # Handle any exceptions that occur and return an error message
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        # Ensure that the database session is closed
        db_session.close()


# -------------------------------------------------------------------------------------------- #
# Professor makes the question visible to the class
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/question/<question_id>/ask", methods=["POST"])
def toggle_question(class_id, question_id):
    session = SessionLocal()
    try:
        data = request.get_json()
        is_active = data.get("active", True)
        
        # Check for an active class session
        active_session = session.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        if not active_session:
            return jsonify({
                "success": False, 
                "message": "No active class session. Please start a session before asking questions."
            }), 403

        # Check if the question is currently displayed
        question_to_update = session.query(Question).filter_by(question_id=question_id, class_id=class_id).first()
        if question_to_update.is_displayed:
            return jsonify({
                "success": False, 
                "message": "This question is currently displayed. Please undisplay it before asking."
            }), 409

        # Check if another question is already active
        if is_active:
            active_question = session.query(Question).filter(
                Question.class_id == class_id,
                Question.is_active == True,
                Question.question_id != question_id
            ).first()
            if active_question:
                return jsonify({
                    "success": False, 
                    "message": "Another question is currently active. Please deactivate it first.",
                    "activeQuestionId": active_question.question_id
                }), 409  

        question_to_update.is_active = is_active
        session.commit()
        if not is_active:
            summary_text, explanations = db_operations.fetch_answers_generate_summary(session, class_id, question_id)
            db_operations.store_summary(session, question_id, summary_text, explanations)

        return jsonify({"success": True, "message": "Question status updated."}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        session.close()

@app.route("/class/<class_id>/active-question", methods=["GET"])
def get_active_question(class_id):
    """
    Retrieves the current active question for a given class. If there is an active question,
    it returns the question details; otherwise, it indicates that there is no active question.
    """
    # Log the class ID for debugging
    print(f"class_id: {class_id}")
    
    # Query the database for active questions related to the specified class
    active_question = db_operations.get_active_questions_for_class(class_id)
    print(f"Active question: {active_question}")
    
    # Check if there is an active question
    if active_question:
        # Prepare the question data for response
        question_data = {
            "question_id": active_question[0].question_id,  # Assuming the first result is the relevant one
            "text": active_question[0].text,
            "correct_answer": active_question[0].correct_answer,
        }
        # Return the question data with success status
        return jsonify({"success": True, "question": question_data})
    else:
        # Return a response indicating no active question
        return jsonify({"success": False, "question": None})
 
# -------------------------------------------------------------------------------------------- #
# Student Answer Submission for Displayed Question
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/submit-answer", methods=["POST"])
def submit_answer(class_id):
    data = request.get_json()
    question_id = data.get("questionId")
    answer_text = data.get("answerText")
    student_id = flask.session.get("username")

    if not db_operations.is_question_active(question_id):
        return jsonify({"success": False, "message": "Question is not active"}), 403

    if not db_operations.is_student_enrolled_in_class(student_id, class_id):
        return (
            jsonify(
                {"success": False, "message": "Student is not enrolled in this class"}
            ),
            403,
        )

    submission_response = db_operations.submit_answer_for_question(
        question_id, student_id, answer_text
    )

    if submission_response == "Answer submitted successfully":
        return jsonify({"success": True, "message": submission_response})
    elif submission_response == "Answer already submitted":
        return jsonify({"success": False, "message": submission_response}), 409
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Failed to submit answer.",
                    "error": submission_response,
                }
            ),
            500,
        )

# -------------------------------------------------------------------------------------------- #
# Professor : See individual student responses
# -------------------------------------------------------------------------------------------- #

@app.route('/class/<class_id>/answers')
def display_answers_for_question(class_id):
    print(f"class_id: {class_id} and I was reached")
    answers, question_text = db_operations.get_answers_for_displayed_question(class_id)
    if answers is None:
        if question_text == "No active session found" or question_text == "No displayed question found":
            answers = []  
        else:
            os.abort(404, description="Resource not found")
    return render_template('answers-page.html', question_text=question_text, answers=answers)


# ============================================================================================ #
# Feature: Generate Feedback from student responses
# ============================================================================================ #

@app.route("/class/<class_id>/feedback")
def class_feedback(class_id):
    db_session = SessionLocal()
    try:
        logged_in_user_id = flask.session.get("username")
        user_role = flask.session.get("role")

        displayed_question = db_session.query(Question).filter_by(class_id=class_id, is_displayed=True).first()
        if not displayed_question:
            return render_template("feedback.html", question_content="No question is currently displayed.", notes = "No question is currently displayed")

        feedback_data = db_operations.get_feedback_data(db_session, class_id, displayed_question.question_id)
        if not feedback_data:
            return render_template("feedback.html", question_content="Question haven't asked yet")

        user_answer_text = "You are an instructor; you don't have a submitted answer."
        if user_role == "student":
            user_answer = (
                db_session.query(Answer)
                .filter_by(question_id=displayed_question.question_id, student_id=logged_in_user_id)
                .first())
            user_answer_text = user_answer.text if user_answer else "No answer submitted."
        feedback_data.update({"user_answer": user_answer_text})
        return render_template("feedback.html", **feedback_data)
    finally:
        db_session.close()
        

# -------------------------------------------------------------------------------------------- #
# Professor : Display Class Feedback to Students
# -------------------------------------------------------------------------------------------- #

@app.route("/class/<class_id>/question/<question_id>/toggle_display", methods=["POST"])
def toggle_display(class_id, question_id):
    session = SessionLocal()
    try:
        data = request.get_json()
        should_display = data.get('displayed', False)
        question = session.query(Question).filter_by(class_id=class_id, question_id=question_id).first()
        if not question:
            return jsonify({"success": False, "message": "Question not found."}), 404
        active_session = session.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        if not active_session:
            return jsonify({
                "success": False,
                "message": "No active class session. Please start a session before displaying questions."
            }), 403
        if should_display and question.is_active:
            return jsonify({
                "success": False,
                "message": "This question is currently active. Please stop it before displaying."
            }), 409
        if should_display:
            currently_displayed_question = session.query(Question).filter(
                Question.class_id == class_id,
                Question.is_displayed == True,
                Question.question_id != question_id
            ).first()
            if currently_displayed_question:
                return jsonify({
                    "success": False,
                    "message": "Another question is currently displayed. Please undisplay it before displaying this one."
                }), 409

        question.is_displayed = should_display
        session.commit()
        return jsonify({
            "success": True,
            "message": f"Question display status updated to {'displayed' if question.is_displayed else 'undisplayed'}.",
            "isDisplayed": question.is_displayed
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        session.close()
        

# ============================================================================================ #
# Feature: Live Chat
# ============================================================================================ #

@app.route("/chat")
def chat():
    username = session.get('username')
    print(username)
    html_code = flask.render_template("chat.html", username=username)
    response = flask.make_response(html_code)
    return response


@socketio.on('send_message')
def handle_send_message(data):
    """
    Handles the event of sending a chat message by a user. It checks for an active class and session,
    assigns the correct user role, creates a new chat message, and broadcasts it to all connected clients.
    If any issue occurs (like no active session), it emits an error message back to the client.
    """
    # Retrieve user ID from the session
    user_id = session.get('username')
    db_session = SessionLocal()  # Initialize database session

    try:
        # Retrieve the active class and session IDs
        class_id, session_id = db_operations.get_active_class_and_session_ids(user_id, db_session)
        if not class_id or not session_id:
            # Emit an error if no active class or session found
            emit('error', {'error': 'No active session or class found.'}, room=request.sid)
            return
        
        # Get the user's role and determine if they are a TA
        role = db_operations.get_user_role(user_id)
        is_ta = db_operations.is_user_a_ta_in_class(user_id, class_id)
        print(f"is_ta: {is_ta}")
        if is_ta:
            role = "TA"  # Assign TA role if applicable
        
        # Create a new chat message instance
        new_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            sender_id=user_id,
            class_id=class_id,
            session_id=session_id,
            text=data.get('content'),
            role=role,
            timestamp=datetime.utcnow()
        )
        db_session.add(new_message)
        db_session.commit()  # Commit the new message to the database
        
        # Emit the new message back to the sender's client
        emit('new_message', {
            'message_id': new_message.message_id,
            'text': new_message.text,
            'sender_id': new_message.sender_id,
            'role': new_message.role,
            'timestamp': new_message.timestamp.isoformat()
        }, room=request.sid)
    
        # Broadcast the new message to all clients except the sender
        emit('new_message', {
            'message_id': new_message.message_id,
            'text': new_message.text,
            'sender_id': new_message.sender_id,
            'role': new_message.role,
            'timestamp': new_message.timestamp.isoformat()
        }, broadcast=True, include_self=False)
    except Exception as e:
        # Rollback the transaction in case of an error
        db_session.rollback()
        emit('error', {'error': str(e)}, room=request.sid)
    finally:
        # Ensure that the database session is closed
        db_session.close()


@app.route('/chat/<class_id>/messages', methods=['GET'])
def fetch_chat_messages(class_id):
    """
    Fetches chat messages for a given class if there is an active session.
    Returns messages ordered by their timestamp and includes the status of the class session.
    It also handles exceptions and ensures database connections are properly closed.
    """
    # Initialize database session
    db_session = SessionLocal()
    try:
        # Query for an active class session based on the class ID
        active_session = db_session.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        is_class_active = bool(active_session)  # Convert to bool for JSON response

        # Handle cases where no active session is found
        if not active_session:
            return jsonify({'success': False, 'isClassActive': is_class_active, 'message': 'No active session for this class.'}), 404

        # Retrieve messages for the active session, ordered by timestamp
        messages = db_session.query(ChatMessage).filter_by(class_id=class_id, session_id=active_session.session_id).order_by(ChatMessage.timestamp.asc()).all()
        current_user_id = session.get('username', 'Unknown')  # Get current user ID from session
        
        # Prepare list of messages for response
        messages_list = [{
            'message_id': message.message_id,
            'sender_id': message.sender_id,
            'text': message.text,
            'role': message.role,
            'timestamp': message.timestamp.isoformat()  # Convert timestamp to ISO format
        } for message in messages]
        
        # Print message list for debugging
        print(f"messages_list: {messages_list}")
        
        # Return success response with message data and class session status
        return jsonify({
            'success': True,
            'isClassActive': is_class_active,
            'messages': messages_list,
            'currentUserId': current_user_id
        })
    except Exception as e:
        # Handle any exceptions that occur during the process
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'success': False, 'isClassActive': False, 'error': str(e)}), 500
    finally:
        # Ensure the database session is closed
        db_session.close()

        
        
# ============================================================================================ #
# Feature: Attendance Tracking
# ============================================================================================ #

@app.route("/attendance/<class_id>/")
def attendance(class_id):
    student_id = flask.session.get("username")
    print(f"Student:{student_id}")
    data = db_operations.get_attendance_and_scores(class_id, student_id)
    print(f"data: {data}")
    if not data:
        flask.flash("Could not retrieve attendance and scores data.", "error")
        return flask.redirect(flask.url_for("dashboard"))
    score_percentage = 0
    attendance_percentage = 0
    if (data['possibleScore'] != 0):
        score_percentage = (data['score'] / data['possibleScore']) * 100
    if (data['totalSessions'] != 0):
        attendance_percentage = (data['attendance'] / data['totalSessions']) * 100
    return flask.render_template("attendance.html", data=data, score_percentage=score_percentage, attendance_percentage=attendance_percentage)


# -------------------------------------------------------------------------------------------- #
# URL Error Page
# -------------------------------------------------------------------------------------------- #

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ============================================================================================ 
# Main
# ============================================================================================ 
if __name__ == '__main__':
    socketio.run(app)
