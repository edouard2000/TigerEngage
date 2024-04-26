#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# app.py
# Authors: Edouard Kwizera, Roshaan Khalid, Jourdain Babisa, Wangari Karani
# --------------------------------------------------------------------------------------------

# Standard library imports
import io
import os
import uuid
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

# Related third-party imports
from dotenv import load_dotenv
import flask
from flask import jsonify, request, flash, redirect, session, url_for, render_template, send_file
from flask_socketio import SocketIO, send, emit
from flask_wtf.csrf import CSRFProtect
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

# Local application/library specific imports
from auth import authenticate
from conciseNotes import LectureNoteSummarizer
from database import ChatMessage, ClassSession, Question, SessionLocal, User, Student, Class, Enrollment, Answer
import db_operations
from req_lib import ReqLib
from summarizer import TextSummarizer

load_dotenv()

# -------------------------------------------
app = flask.Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", "123456")
csrf = CSRFProtect(app)
socketio = SocketIO(app, cors_allowed_origins="*")

database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url.replace(
        "postgres://", "postgresql://"
    )
else:
    print("The DATABASE_URL environment variable is not set.")
# -------------------------------------------
@app.route("/", methods=["GET"])
def index():
    if 'visited' in session:
        return redirect(url_for("authenticate_and_direct"))
    return redirect(url_for("get_started"))

@app.route("/get-started", methods=["GET"])
def get_started():
    username = authenticate()
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response

@app.route("/home", methods=["GET"])
def home():
    if 'role' in session:
        role = flask.session['role']
        if role == 'student':
            return redirect(url_for("student_dashboard"))
        elif role == 'professor':
            username = flask.session['username']
            class_id = db_operations.get_professors_class_id(username)
            return redirect(url_for("professor_dashboard", class_id=class_id))
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response


@app.route("/logout", methods=["GET"])
def logout():
    db = SessionLocal()
    try:
        user_id = flask.session.get("username")
        if user_id:
            # Check if the user has an active class session
            active_session = (
                db.query(ClassSession)
                .join(Class, ClassSession.class_id == Class.class_id)
                .filter(Class.instructor_id == user_id, ClassSession.is_active == True)
                .first()
            )
            if active_session:
                return jsonify({
                    "success": False,
                    "message": "There is an active session. Please end the session before logging out."
                }), 400

        flask.session.clear()
        return jsonify({"success": True, "message": "You have been logged out successfully."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()




@app.route("/role-selection")
def role_selection():
    html_code = flask.render_template("role-selection.html")
    response = flask.make_response(html_code)
    return response


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

@app.route("/questions")
def questions():
    html_code = flask.render_template("Question.html")
    response = flask.make_response(html_code)
    return response

@app.route("/class_dashboard/<class_id>")
def class_dashboard(class_id):
    with SessionLocal() as session:
        class_info = session.query(Class).filter(Class.class_id == class_id).first()
        if class_info:
            class_name = class_info.title
        else:
            class_name = "Class not found"
    return render_template("class-dashboard.html", class_name=class_name)


@app.route("/professor_dashboard/<class_id>")
def professor_dashboard(class_id):
    username = flask.session.get("username")
    if not username:
        return flask.redirect(url_for("home"))
    req_lib = ReqLib()

    display_name = req_lib.getJSON(
        req_lib.configs.USERS,
        uid=username,
    )

    display_name = display_name[0].get('displayname')
    course_name = db_operations.get_professor_class(username)
    return flask.render_template(
        "professor-dashboard.html",
        course_name=course_name,
        username=display_name,
        class_id=class_id,
    )


@app.route("/edit_student/<class_id>/<user_id>", methods=["GET", "POST"])
def edit_user(class_id, user_id):
    db_session = SessionLocal()
    student = db_session.query(Student).filter_by(user_id=user_id).first()

    if student is None:
        db_session.close()
        flash("Student not found.", "error")
        return redirect(url_for("class_userlist", class_id=class_id))

    enrollment = db_session.query(Enrollment).filter_by(student_id=user_id).first()
    
    if request.method == "POST":
        if enrollment:
            enrollment.score = request.form.get("score", enrollment.score)
            enrollment.is_ta = bool(int(request.form.get("is_ta", enrollment.is_ta)))
            db_session.commit()
            flash("Student information updated successfully.", "success")
        else:
            flash("Enrollment information not found.", "error")
        return redirect(url_for("professor_dashboard", class_id=class_id))

    db_session.close()
    return render_template("edit_student.html", student=student, class_id=class_id, score=enrollment.score if enrollment else None, is_ta=enrollment.is_ta if enrollment else None)


@app.route("/delete_user/<class_id>/<user_id>", methods=["POST"])
def delete_user(class_id, user_id):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(user_id=user_id).first()

    if user:
        delete_enrollment = db_session.query(Enrollment).filter(Enrollment.student_id == user_id).first()
        db_session.delete(delete_enrollment)
        
        db_session.commit()
        flash("User successfully deleted", "success")
    else:
        flash("User not found.", "error")
    db_session.close()

    return redirect(url_for("professor_dashboard", class_id=class_id))


@app.route("/class/<class_id>/userlist")
def class_userlist(class_id):
    try:
        users_data = db_operations.get_students_for_class(class_id)
        return render_template("class-users.html", users=users_data, class_id=class_id)
    except Exception as e:
        print(e)
        return (
            jsonify({"success": False, "message": "Unable to fetch class users"}),
            500,
        )


@app.route("/select_role", methods=["POST"])
def select_role():
    role = request.json["role"]
    flask.session["role"] = role
    return jsonify({"success": True, "redirectUrl": url_for("authenticate_and_direct")})


@app.route("/authenticate_and_direct", methods=["GET"])
def authenticate_and_direct():
    username = authenticate()
    flask.session["username"] = username
    actual_role = db_operations.get_user_role(username)

    if actual_role:
        flask.session["actual_role"] = actual_role
        if actual_role != flask.session.get("role"):
            flash(f"Access denied. Your role is {actual_role}.", "error")
            return flask.redirect(flask.url_for("get_started"))

        flask.session['visited'] = True
        if actual_role == "professor":
            class_id = db_operations.get_professors_class_id(username)
            if not class_id:
                print(f"No class associated with the professor {username}")
                return flask.redirect(flask.url_for("create_class_form"))
            flask.session['class_id'] = class_id  
            return flask.redirect(flask.url_for("professor_dashboard", class_id=class_id))
        
        
        elif actual_role == "student":
            class_id = db_operations.get_students_class_id(username)
            if not class_id:
                print(f"No class associated with the student {username}")
                return flask.redirect(url_for("student_dashboard"))
            flask.session['class_id'] = class_id 
            return flask.redirect(flask.url_for("student_dashboard", class_id=class_id))
    else:
        role = flask.session.get("role", "student")
        print(
            f"{username} does not exist in the database, creating one with role {role}"
        )
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


@app.route("/create_class_form", methods=["GET"])
def create_class_form():
    return flask.render_template("create_class_form.html")


@app.route("/create_class", methods=["POST"])
def create_class():
    class_name = request.form.get("class_name")
    username = flask.session.get("username")
    success, class_id_returned = db_operations.create_class_for_professor(
        username, class_name
    )
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Class successfully created!',
            'class_id': class_id_returned
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Error creating class.'
        }), 400


@app.route("/add-question")
def add_question():
    """this method will render a form with input to add questions

    Returns:
        _type_: render template
    """
    return flask.render_template("add-question.html")


@app.route("/class/<class_id>/add-question", methods=["POST"])
def add_question_to_class_route(class_id):
    data = request.json
    question_text = data.get("question_text")
    correct_answer = data.get("correct_answer")

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
    success = db_operations.add_question_to_class(
        class_id, question_text, correct_answer
    )

    if success:
        return jsonify({"success": True, "message": "Question successfully added."})
    else:
        return jsonify({"success": False, "message": "Failed to add question."}), 500


@app.route("/class/<class_id>/questions", methods=["GET"])
def get_questions_for_class_route(class_id):
    results = db_operations.get_questions_for_class(class_id)
    if results:
        return jsonify({"success": True, "questions": results})
    else:
        return (
            jsonify(
                {"success": False, "message": "No questions found for this class."}
            ),
            404,
        )


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

    textobject = p.beginText(72, height - 100)  
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
    
    
@app.route("/search_classes", methods=["GET"])
def search_classes():
    if "username" not in session:
        return jsonify({"success": False, "message": "User not authenticated"}), 401

    db = SessionLocal()
    try:
        search_term = request.args.get("search", "").lower()
        if not search_term:
            return (
                jsonify({"success": False, "message": "Search term is required"}),
                400,
            )
        classes = db.query(Class).filter(Class.title.ilike(f"%{search_term}%")).all()

        classes_data = [
            {
                "id": cls.class_id,
                "name": cls.title,
                "instructor": cls.instructor.user_id,
            }
            for cls in classes
        ]

        return jsonify({"success": True, "classes": classes_data})
    finally:
        db.close()


@app.route("/enroll_in_class", methods=["POST"])
def enroll_in_class():
    username = session.get("username")
    class_id = request.json.get("class_id")
    if not username and class_id:
        return jsonify({"success": False, "message": "User not authenticated"}), 401

    db = SessionLocal()
    try:
        user = db.query(User).filter_by(user_id=username).first()
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user_id = user.user_id

        existing_enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user_id, class_id=class_id)
            .first()
        )
        if existing_enrollment:
            return jsonify({"success": False, "message": "Already enrolled"}), 400

        enrollment = Enrollment(
            enrollment_id=str(uuid.uuid4()), student_id=user_id, class_id=class_id
        )
        db.add(enrollment)
        db.commit()
        return jsonify({"success": True, "message": "Enrolled successfully"})
    except NoResultFound:
        return jsonify({"success": False, "message": "Class not found"}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()


@app.route("/unenroll_from_class", methods=["POST"])
def unenroll_from_class():
    user_id = flask.session.get("username")
    if not user_id:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    data = request.get_json()
    class_id = data.get("class_id")
    if not class_id:
        return jsonify({"success": False, "message": "Class ID is required"}), 400
    db = SessionLocal()
    try:
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user_id, class_id=class_id)
            .first()
        )
        if not enrollment:
            return jsonify({"success": False, "message": "Enrollment not found"}), 404
        db.delete(enrollment)
        db.commit()
        return jsonify({"success": True, "message": "Unenrolled successfully"})
    except Exception as e:
        db.rollback()
        return (
            jsonify({"success": False, "message": "Unenrollment failed: " + str(e)}),
            500,
        )
    finally:
        db.close()


@app.route("/get_enrolled_classes")
def get_enrolled_classes():
    username = flask.session.get("username")
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    classes_data = db_operations.get_student_classes(username)
    if not classes_data:
        print("No classes found for user:", username)
        return (
            jsonify({"success": False, "message": "No classes found for this user."}),
            404,
        )
    return jsonify({"success": True, "classes": classes_data})



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

    except db_exc.SQLAlchemyError as e:
        db.rollback()
        return jsonify({"success": False, "message": "Database error: " + str(e)}), 500
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": "Error: " + str(e)}), 500
    finally:
        db.close()



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



@app.route("/class/<class_id>/session_status", methods=["GET"])
def check_class_session_status(class_id):
    with SessionLocal() as session:
        active_session = (
            session.query(ClassSession)
            .filter_by(class_id=class_id, is_active=True)
            .first()
        )
        return jsonify({"isActive": active_session is not None})


@app.route("/class/<class_id>/check_in", methods=["POST"])
def check_in(class_id):
    username = flask.session.get("username")
    if not username:
        return jsonify({"success": False, "message": "User not authenticated"}), 401
    if not db_operations.is_student_enrolled_in_class(username, class_id):
        return (
            jsonify(
                {"success": False, "message": "Student not enrolled in this class"}
            ),
            403,
        )
    active_session = db_operations.get_active_session_for_class(class_id)
    if not active_session:
        return (
            jsonify({"success": False, "message": "No active session for this class"}),
            404,
        )
    if db_operations.has_checked_in(username, active_session.session_id):
        return jsonify(
            {
                "success": True,
                "message": "Already checked in.",
                "redirectUrl": url_for("class_dashboard", class_id=class_id),
            }
        )

    success, message = db_operations.record_attendance_and_update(
        username, class_id, active_session.session_id
    )
    if success:
        return jsonify(
            {
                "success": True,
                "message": "Check-in successful.",
                "redirectUrl": url_for("class_dashboard", class_id=class_id),
            }
        )
    else:
        return jsonify({"success": False, "message": message}), 500
    

@app.route("/class/<class_id>/question/<question_id>/status", methods=["GET"])
def get_question_status(class_id, question_id):
    db_session = SessionLocal()
    try:
        question = db_session.query(Question).filter_by(
            class_id=class_id, question_id=question_id).first()
        if not question:
            return jsonify({"success": False, "message": "Question not found."}), 404

        return jsonify({
            "success": True,
            "isActive": question.is_active,
            "isDisplayed": question.is_displayed
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db_session.close()


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

@app.route("/class/<string:class_id>/question/<string:question_id>/edit", methods=["POST"])
def edit_question(class_id, question_id):
    data = request.get_json()
    print(data)
    db = SessionLocal()
    try:
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        if question:
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

            question.text = data["question_text"]
            question.correct_answer = data["correct_answer"]
            db.commit()
            return jsonify(
                {"success": True, "message": "Question updated successfully."}
            )
        else:
            return jsonify({"success": False, "message": "Question not found."}), 404
    finally:
        db.close()


@app.route("/class/<string:class_id>/question/<string:question_id>/delete", methods=["DELETE"])
def delete_question(class_id, question_id):
    db = SessionLocal()
    try:
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        if question:
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
            
            db.delete(question)
            db.commit()
            return jsonify({"success": True, "message": "Question deleted successfully."})
        else:
            return jsonify({"success": False, "message": "Question not found."}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()



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

@app.route("/class/<class_id>/active-question", methods=["GET"])
def get_active_question(class_id):
    active_question = db_operations.get_active_questions_for_class(class_id)
    if active_question:
        question_data = {
            "question_id": active_question[0].question_id,
            "text": active_question[0].text,
            "correct_answer": active_question[0].correct_answer,
        }
        return jsonify({"success": True, "question": question_data})
    else:
        return jsonify({"success": False, "question": None}), 404


@app.route("/attendance/<class_id>/")
def attendance(class_id):
    student_id = flask.session.get("username")
    data = db_operations.get_attendance_and_scores(class_id, student_id)
    if not data:
        flask.flash("Could not retrieve attendance and scores data.", "error")
        return flask.redirect(flask.url_for("dashboard"))
    return flask.render_template("attendance.html", data=data)


#
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
        

@app.route("/class/<class_id>/question/<question_id>/toggle_display", methods=["POST"])
def toggle_display(class_id, question_id):
    session = SessionLocal()
    try:
        data = request.get_json()
        should_display = data.get('displayed', False)
        
        # Fetch the question to be updated
        question = session.query(Question).filter_by(class_id=class_id, question_id=question_id).first()
        if not question:
            return jsonify({"success": False, "message": "Question not found."}), 404

        # Check if a class session is currently active
        active_session = session.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        if not active_session:
            return jsonify({
                "success": False,
                "message": "No active class session. Please start a session before displaying questions."
            }), 403

        # Check if the question is currently active and the request is to display it
        if should_display and question.is_active:
            return jsonify({
                "success": False,
                "message": "This question is currently active. Please stop it before displaying."
            }), 409

        # Check if another question is already displayed when trying to display this one
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
        

@app.route("/chat")
def chat():
    html_code = flask.render_template("chat.html")
    response = flask.make_response(html_code)
    return response


@socketio.on('send_message')
def handle_send_message(data):
    user_id = session.get('username')
    db_session = SessionLocal()

    class_id, session_id = db_operations.get_active_class_and_session_ids(user_id, db_session)

    if not class_id or not session_id:
        emit('error', {'error': 'No active session or class found for the user.'})
        return

    content = data.get('content')
    if not content:
        emit('error', {'error': 'Message content cannot be empty.'})
        return

    try:
        new_message = ChatMessage(
            message_id=str(uuid.uuid4()),
            sender_id=user_id,
            class_id=class_id,
            session_id=session_id,
            text=content,
            timestamp=datetime.now(ZoneInfo("UTC"))
        )
        db_session.add(new_message)
        db_session.commit()
        emit('receive_message', {'content': content}, broadcast=True)
    except Exception as e:
        db_session.rollback()
        emit('error', {'error': f'Failed to save message: {str(e)}'})
    finally:
        db_session.close()


@app.route('/chat/<class_id>/messages', methods=['GET'])
def fetch_chat_messages(class_id):
    db_session = SessionLocal()
    try:
        active_session = (
            db_session.query(ClassSession)
            .filter_by(class_id=class_id, is_active=True)
            .first()
        )
        if not active_session:
            print(f"No active session found for class ID: {class_id}")
            return jsonify({'success': False, 'message': 'No active session for this class.'}), 404
        messages = (
            db_session.query(ChatMessage)
            .filter_by(class_id=class_id, session_id=active_session.session_id)
            .order_by(ChatMessage.timestamp.asc())
            .all()
        )
        messages_list = [
            {
                'message_id': message.message_id,
                'sender_id': message.sender_id,
                'text': message.text,
                'timestamp': message.timestamp.isoformat()
            } for message in messages
        ]
        return jsonify({'success': True, 'messages': messages_list})
    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        db_session.close()

