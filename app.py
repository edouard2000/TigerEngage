#!/usr/bin/env python

#-----------------------------------------------------------------------
# auth.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero
#-----------------------------------------------------------------------

import os
import uuid # Import the uuid module to generate unique IDs
import auth
import flask
from flask import request, flash, redirect, url_for, render_template
from psycopg2 import IntegrityError
import auth
from database import SessionLocal, User
from testUsers import fetch_all_users


app = flask.Flask(__name__)

app.secret_key = os.environ["APP_SECRET_KEY"]

classes = [
    {
        "id": 1,
        "name": "Introduction to Python",
        "instructor": "Prof. John Doe",
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Advanced Mathematics",
        "instructor": "Dr. Jane Smith",
        "is_active": False,
    },
]

students = [{"id": 7, "netid": "ek4249"}]


def check_netid_exists(netid_to_check, students):
    for student in students:
        if student["netid"] == netid_to_check:
            return True
    return False


student = [
    {
        "id": 1,
        "name": "Alice Johnson",
        "score": 88,
    },
    {
        "id": 2,
        "name": "Bob Smith",
        "score": 92,
    },
]


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response

@app.route("/role-selection")
def role_selection():
    html_code = flask.render_template("role-selection.html")
    response = flask.make_response(html_code)
    return response

@app.route("/login")
def login():
    html_code = flask.render_template('login.html')
    response = flask.make_response(html_code)
    return response

# @app.route("/login")
# def caslogin_buttonslot():
#     html_code = flask.render_template('login.html')
#     response = flask.make_response(html_code)
#     return response

@app.route("/register")
def register():
    html_code = flask.render_template('register.html')
    response = flask.make_response(html_code)
    return response

# Route to handle the form submission for registration



@app.route('/register', methods=['POST'])
def process_registration():
    db_session = SessionLocal()
    
    user_id = str(uuid.uuid4()) 
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    password = request.form['password']

    new_user = User(user_id=user_id, email=email, password_hash=password, role='student', name=f"{first_name} {last_name}")
    
    try:
        db_session.add(new_user)
        db_session.commit()
        return redirect(url_for('home'))
    except IntegrityError as e:
        db_session.rollback()
        return render_template('error_page.html', error=str(e))
    finally:
        db_session.close()


@app.route("/new_student_dashboard1/<name>")
def new_student_dashboard(name):
    auth.authenticate()
    html_code = flask.render_template(
        "student-dashboard.html",
        student_name=name,
        classes = classes
    )
    response = flask.make_response(html_code)
    return response

@app.route("/student_dashboard")
def student_dashboard():
    username = auth.authenticate()
    if check_netid_exists(username, students):
        html_code = flask.render_template(
            "student-dashboard.html", username=username, classes=classes
        )
        response = flask.make_response(html_code)
        return response
    else:
        html_code = flask.render_template(
            "denied.html",
        )
        response = flask.make_response(html_code)
        return response


@app.route("/chat")
def chat():
    html_code = flask.render_template("chat.html")
    response = flask.make_response(html_code)
    return response


@app.route("/questions")
def questions():
    html_code = flask.render_template("Question.html")
    response = flask.make_response(html_code)
    return response

# Route to handle the form submission for student responses to a question
@app.route("/questions", methods=['POST'])
def studentresponse():
    # Generate a unique answer_id
    answer_id = str(uuid.uuid4())

    # Fetch data from the form
    user_id = flask.request.form['user_id']
    answer_id = flask.request.form['answer_id']
    question_id = flask.request.form['question_id']
    student_answer = flask.request.form['student_answer']

    # Store student response in database
    new_answer = database.Answer(answer_id=answer_id, question_id=question_id, user_id=user_id, text=student_answer)
    session.add(new_answer)

    try:
        # Attempt to commit the session
        session.commit()
        # If the answer is successfully submitted, display "submission received"
        return flask.redirect(flask.url_for('feedback', user_answer=student_answer))
    except IntegrityError as e:
        # Rollback the session to prevent further errors
        session.rollback()

        # Handle the unique constraint violation error
        error_message = "Your submission was not submitted successfully"
        # You can log the error or display a user-friendly message
        print(e + ": " + error_message)
        # print(f"Error: {}")
        # return flask.render_template('', error_message=error_message) 
        html_code = flask.render_template("Question.html")
        response = flask.make_response(html_code)
        return response    

@app.route("/feedback")
def feedback():
    feedback_data = {
        "question_content": "What is the capital of France?",
        "answers_summary": "Most students answered correctly that the capital of France is Paris.",
        "correct_answer": "The correct answer is Paris.",
        "user_answer": "Your answer was Paris.",
    }
    return flask.render_template("feedback.html", **feedback_data)


@app.route("/class_dashboard/<int:class_id>")
def class_dashboard(class_id):
    class_info = next((c for c in classes if c["id"] == class_id), None)
    if class_info:
        class_name = class_info["name"]
    else:
        class_name = "Class not found"
    return flask.render_template("class-dashboard.html", class_name=class_name)


@app.route("/attendance")
def default_attendance():
    default_class_id = 1
    return attendance(default_class_id)


@app.route("/attendance/<int:class_id>")
def attendance(class_id):
    class_info = next((c for c in classes if c["id"] == class_id), None)
    if class_info:
        class_name = class_info["name"]
    else:
        class_name = "Class not found"
    return flask.render_template("attendance.html", class_name=class_name)


@app.route("/professor_dashboard")
def professor_dashboard():
    prof_name = "Prof. John Doe"
    return flask.render_template("professor-dashboard.html", prof_name=prof_name)



@app.route("/edit_student/<user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(user_id=user_id).first()

    if user is None:
        db_session.close()
        flash("Student not found.", "error")
        return redirect(url_for("userlist"))

    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.score = float(request.form.get("score", 0))
        db_session.commit()
        flash("Student information updated successfully.", "success")
        return redirect(url_for("userlist"))

    db_session.close()
    return render_template("edit_student.html", student=user)



@app.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(user_id=user_id).first()
    if user:
        db_session.delete(user)
        db_session.commit()
        flash("Student successfully deleted", "success")
    else:
        flash("Student not found.", "error")

    db_session.close()
    return redirect(url_for("userlist"))



@app.route("/userlist")
def userlist():
    prof_name = "Prof. John Doe"
    users = fetch_all_users()
    print("Users to be displayed:", users)
    return flask.render_template("class-users.html", users=users, prof_name=prof_name)

@app.route("/add-question")
def add_question():
    return flask.render_template("add-question.html")


# @app.route("/add-question")
# def add_question():
#     db_session = SessionLocal()
#     question_text = request.form.get("question_text")
#     answer_text = request.form.get("answer_text")
    
#     question = Question(question_text=question_text, answer_text=answer_text)
#     db_session.add(question)
#     try:
#         db_session.commit()
#         return jsonify(success=True)
#     except Exception as e:
#         db_session.rollback()
#         return jsonify(success=False, error=str(e))
#     finally:
#         db_session.close()


@app.route("/logoutapp", methods=["GET"])
def logoutapp():
    return auth.logoutapp()


@app.route("/logoutcas", methods=["GET"])
def logoutcas():
    return auth.logoutcas()

if __name__ == "__main__":
    app.run(debug=True)
