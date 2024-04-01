#!/usr/bin/env python

# -----------------------------------------------------------------------
# auth.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero
# -----------------------------------------------------------------------

import os
import uuid
from zoneinfo import ZoneInfo 
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import flask
from sqlalchemy.exc import SQLAlchemyError
from flask import (
    jsonify, request, flash, redirect, url_for, render_template
)

from auth import authenticate
from database import ClassSession, SessionLocal, User,Class
from testUsers import fetch_all_users

app = flask.Flask(__name__)

app.secret_key = os.environ["APP_SECRET_KEY"]
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("postgres://", "postgresql://")



@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():
    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response


@app.route("/role-selection")
def role_selection():
    html_code = flask.render_template("role-selection.html")
    response = flask.make_response(html_code)
    return response


@app.route("/student_dashboard")
def student_dashboard():
     username = flask.session.get('username')
     classes = get_student_classes(username)
     html_code = flask.render_template(
         "student-dashboard.html", student=username, classes=classes
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



@app.route("/feedback")
def feedback():
    feedback_data = {
        "question_content": "What is the capital of France?",
        "answers_summary": "Most students answered correctly that the capital of France is Paris.",
        "correct_answer": "The correct answer is Paris.",
        "user_answer": "Your answer was Paris.",
    }
    return flask.render_template("feedback.html", **feedback_data)


@app.route("/class_dashboard/<class_id>")
def class_dashboard(class_id):
    with SessionLocal() as session:
        class_info = session.query(Class).filter(Class.class_id == class_id).first()
        if class_info:
            class_name = class_info.title
        else:
            class_name = "Class not found"
    return render_template("class-dashboard.html", class_name=class_name)


@app.route("/attendance")
def default_attendance():
    default_class_id = 1
    return attendance(default_class_id)


@app.route("/attendance/<int:class_id>")
def attendance(class_id):
    pass
    
@app.route("/professor_dashboard")
def professor_dashboard():
    username = flask.session.get('username')
    return flask.render_template("professor-dashboard.html", prof_name=username)


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
    users = fetch_all_users()
    print("Users to be displayed:", users)
    return flask.render_template("class-users.html", users=users)


@app.route("/add-question")
def add_question():
    return flask.render_template("add-question.html")


@app.route('/class/<class_id>/start_session', methods=['POST'])
def start_class_session(class_id):
    db = SessionLocal()
    new_session = ClassSession(
        class_id=class_id,
        start_time=datetime.now(ZoneInfo("UTC")),
        is_active=True
    )
    db.add(new_session)
    db.commit()

    return jsonify({'success': True, 'message': 'Class session started'})


@app.route('/select_role', methods=['POST']) 
def select_role():
    role = request.json['role']
    flask.session['role'] = role
    return jsonify({'success': True, 'redirectUrl': url_for('authenticate_and_direct')})



@app.route('/authenticate_and_direct', methods=['GET'])
def authenticate_and_direct():
    username = authenticate()  
    flask.session['username'] = username
    
    role = flask.session.get('role', 'student') 
    
    if not user_exists(username):
        create_user(username, role)  
    
    dashboard_url = 'professor_dashboard' if role == 'professor' else 'student_dashboard'
    
    if role == "professor" and not has_classes(username):
        print(f"{username} has no class yet")  
        return flask.redirect(flask.url_for('create_class_form'))
    print(f"{username} has a class already and we are directing to dashboard")
    return flask.redirect(flask.url_for(dashboard_url))

            

@app.route('/create_class_form', methods=['GET'])
def create_class_form():
    return flask.render_template('create_class_form.html')


@app.route('/create_class', methods=['POST'])
def create_class():
    class_name = request.form.get('class_name')
    username = flask.session.get('username')
    if create_class_for_professor(username, class_name):
        return flask.redirect(flask.url_for('professor_dashboard'))
    else:
        flash("Error creating class.", "error")
        return flask.redirect(flask.url_for('create_class_form'))
    
    

# some helper functions

def create_user(netid, role):
    """
    Adjusted to ensure proper session management.
    """
    with SessionLocal() as session:
        email = f"{netid}@princeton.edu"
        new_user = User(user_id=netid, email=email, role=role, netid=netid)
        session.add(new_user)
        try:
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error adding user to database: {e}")
            session.rollback()
            return False
        
        
def create_class_for_professor(netid, title):
    """
    Creates a new class for a professor.
    
    :param netid: The netid of the professor.
    :param title: The title of the class.
    :return: True if the class was created successfully, False otherwise.
    """
    with SessionLocal() as session:
        professor = session.query(User).filter_by(user_id=netid).first()
        if not professor:
            print(f"No professor found with netID: {netid}")
            return False
        
        new_class = Class(
            class_id=str(uuid.uuid4()), 
            title=title,
            instructor_id=netid,
            total_sessions_planned=0, 
            possible_scores=0
        )
        session.add(new_class)
        try:
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error adding class to database: {e}")
            session.rollback()
            return False
        
        

def user_exists(user_id):
    with SessionLocal() as session:
        user = session.query(User).filter_by(user_id=user_id).first()
        return user is not None


def has_classes(username):
    with SessionLocal() as session:
        class_count = session.query(Class).filter_by(instructor_id=username).count()
        return class_count > 0
        

def get_student_classes(username: str) -> list:
    """
    Retrieves a list of classes a student is enrolled in by their username.
    
    :param username: The username (user_id) of the student.
    :return: A list of Class objects the student is enrolled in.
    """
    with SessionLocal() as db_session: 
        user = db_session.query(User).filter(User.user_id == username).first()
        if not user:
            return [] 
        enrolled_classes = [enrollment.class_ for enrollment in user.enrollments]
        return enrolled_classes
    


if __name__ == "__main__":
    app.run(debug=True)

