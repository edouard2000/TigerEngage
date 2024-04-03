#!/usr/bin/env python

# -----------------------------------------------------------------------
# auth.py
# Authors: Alex Halderman, Scott Karlin, Brian Kernighan, Bob Dondero
# -----------------------------------------------------------------------

import os
from zoneinfo import ZoneInfo
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import flask
from flask import jsonify, request, flash, redirect, url_for, render_template
from auth import authenticate
import db_operations
from database import ClassSession, SessionLocal, User, Class


app = flask.Flask(__name__)

app.secret_key = os.environ["APP_SECRET_KEY"]
csrf = CSRFProtect(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace(
    "postgres://", "postgresql://"
)


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
    username = flask.session.get("username")
    classes = db_operations.get_student_classes(username)
    html_code = flask.render_template(
        "student-dashboard.html", student_name=username, classes=classes
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


@app.route("/professor_dashboard/<class_id>")
def professor_dashboard(class_id):
    username = flask.session.get("username")
    course_name = db_operations.get_professor_class(username)
    return flask.render_template(
        "professor-dashboard.html",
        course_name=course_name,
        username=username,
        class_id=class_id,
    )


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
    class_id = flask.session.get("class_id")
    users = db_operations.get_students_for_class(class_id)
    for user in users:
        user["percentage"] = db_operations.computer_precentage_score(
            user["score"], user["possible_scores"]
        )
    return flask.render_template("class-users.html", users=users)


@app.route("/class/<class_id>/start_session", methods=["POST"])
def start_class_session(class_id):
    db = SessionLocal()
    new_session = ClassSession(
        class_id=class_id, start_time=datetime.now(ZoneInfo("UTC")), is_active=True
    )
    db.add(new_session)
    db.commit()

    return jsonify({"success": True, "message": "Class session started"})


@app.route("/select_role", methods=["POST"])
def select_role():
    role = request.json["role"]
    print(f"we got a role: {role}")
    flask.session["role"] = role
    print("we are now redirecting")
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
            return flask.redirect(flask.url_for("home"))

        if actual_role == "professor":
            class_id = db_operations.get_professors_class_id(username)
            if not class_id:
                print(f"{username} has no class yet")
                return flask.redirect(flask.url_for("create_class_form"))
            return flask.redirect(
                flask.url_for("professor_dashboard", class_id=class_id)
            )
        else:
            return flask.redirect(flask.url_for("student_dashboard"))
    else:
        role = flask.session.get("role", "student")
        print(
            f"{username} does not exist in the database, creating one with role {role}"
        )
        db_operations.create_user(username, role)
        dashboard_url = (
            "professor_dashboard" if role == "professor" else "student_dashboard"
        )

        return flask.redirect(flask.url_for(dashboard_url))


@app.route("/create_class_form", methods=["GET"])
def create_class_form():
    return flask.render_template("create_class_form.html")


@app.route("/create_class", methods=["POST"])
def create_class():
    class_name = request.form.get("class_name")
    username = flask.session.get("username")
    if db_operations.create_class_for_professor(username, class_name):
        return flask.redirect(flask.url_for("professor_dashboard"))
    else:
        flash("Error creating class.", "error")
        return flask.redirect(flask.url_for("create_class_form"))


@app.route("/add-question")
def add_question():
    print("do you go here?")
    return flask.render_template("add-question.html")


@app.route("/class/<class_id>/add-question", methods=["POST"])
def add_question_to_class_route(class_id):
    data = request.json
    print("here")
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


if __name__ == "__main__":
    app.run(debug=True)
