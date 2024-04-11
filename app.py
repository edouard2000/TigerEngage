#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# app.py
# Authors: Edouard Kwizera, Roshaan Khalid, Jourdain Babisa, Wangari Karani
# --------------------------------------------------------------------------------------------

import os
import uuid
from datetime import datetime
from auth import authenticate
from flask_wtf.csrf import CSRFProtect
import flask
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import NoResultFound
from flask import jsonify, request, flash, redirect, session, url_for, render_template
from database import ClassSession, Question, SessionLocal, User, Class, Enrollment
import db_operations
from req_lib import ReqLib

# -------------------------------------------

app = flask.Flask(__name__)
app.secret_key = os.environ["APP_SECRET_KEY"]
csrf = CSRFProtect(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL").replace(
    "postgres://", "postgresql://"
)
# -------------------------------------------


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
    if not username:
        return flask.redirect(url_for("home"))
    req_lib = ReqLib()

    username = req_lib.getJSON(
        req_lib.configs.USERS,
        uid=username,
    )

    username = username[0].get('displayname')
    return flask.render_template("student-dashboard.html", student_name=username)


@app.route("/chat")
def chat():
    html_code = flask.render_template("chat.html")
    response = flask.make_response(html_code)
    return response


@app.route("/questions")
def questions():
    # do we have an action in question.html with method=POST, that adds this user/student's answer to the answers table?
    html_code = flask.render_template("Question.html")
    response = flask.make_response(html_code)
    return response


# @app.route("/feedback")
# def feedback():
#     # feedback_data = {
#     #     "question_content": "What is the capital of France?",
#     #     "answers_summary": "Most students answered correctly that the capital of France is Paris.",
#     #     "correct_answer": "The correct answer is Paris.",
#     #     "user_answer": "Your answer was Paris.",
#     # }

#     # need to get the classid to get question data
#     classid = flask.session.get("classes.class_id")
#     question, correct_answer = db_operations.get_questions_for_class(class_id=classid)
#     user_id = flask.session.get("user_id")
#     question_id = flask.session.get("question_id")
#     user_answer, student_answers = db_operations.get_answers(user_id, question_id)

#     summarized_feedback = GenerateFeedback.answers_summary(correct_answer=correct_answer, list_of_student_answers=student_answers)

#     html_code = flask.render_template("feedback.html", question_content=question, answers_summary=summarized_feedback, correct_answer=correct_answer, user_answer=user_answer,)
#     response = flask.make_response(html_code)
#     return response


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
    print("Professor dashboard")
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
    user = db_session.query(User).filter_by(user_id=user_id).first()

    if user is None:
        db_session.close()
        flash("Student not found.", "error")
        return redirect(url_for("class_userlist", class_id=class_id))

    if request.method == "POST":
        user.name = request.form.get("name", user.name)
        user.score = float(request.form.get("score", user.score))
        db_session.commit()
        flash("Student information updated successfully.", "success")
        return redirect(url_for("class_userlist", class_id=class_id))

    db_session.close()
    return render_template("edit_student.html", student=user, class_id=class_id)


@app.route("/delete_user/<class_id>/<user_id>", methods=["POST"])
def delete_user(class_id, user_id):
    db_session = SessionLocal()
    user = db_session.query(User).filter_by(user_id=user_id).first()

    if user:
        db_session.delete(user)
        db_session.commit()
        flash("User successfully deleted", "success")
    else:
        flash("User not found.", "error")
    db_session.close()

    return redirect(url_for("class_userlist", class_id=class_id))


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
                print(f"{username} has no class yet, so let create one")
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
        if role == "professor":
            class_id = db_operations.get_professors_class_id(username)
            if not class_id:
                print(f"{username} has no class yet")
                return flask.redirect(flask.url_for("create_class_form"))
            dashboard_url = "professor_dashboard"
            return flask.redirect(flask.url_for(dashboard_url, class_id=class_id))
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
        return flask.redirect(
            flask.url_for("professor_dashboard", class_id=class_id_returned)
        )
    else:
        flash("Error creating class.", "error")
        return flask.redirect(flask.url_for("create_class_form"))


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
    print(f"this is results: {results}")
    if results:
        return jsonify({"success": True, "questions": results})
    else:
        return (
            jsonify(
                {"success": False, "message": "No questions found for this class."}
            ),
            404,
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

    print(f"username: {username}, class_id: {class_id}")

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
        active_session = (
            db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        )
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

        return (
            jsonify(
                {"success": True, "message": "Class session started successfully."}
            ),
            200,
        )
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()


@app.route("/class/<class_id>/end_session", methods=["POST"])
def end_class_session(class_id):
    db = SessionLocal()
    try:
        active_session = (
            db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        )
        if not active_session:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "No active session found for this class",
                    }
                ),
                404,
            )
        active_session.is_active = False
        active_session.end_time = datetime.now()

        db.commit()

        return (
            jsonify({"success": True, "message": "Class session ended successfully."}),
            200,
        )
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


@app.route("/class/<class_id>/question/<question_id>/ask", methods=["POST"])
def toggle_question(class_id, question_id):
    try:
        data = request.get_json()
        is_active = data.get("active", True)

        with SessionLocal() as session:
            if is_active:
                session.query(Question).filter(
                    Question.class_id == class_id, Question.is_active.is_(True)
                ).update({Question.is_active: False}, synchronize_session="fetch")

            question_to_update = (
                session.query(Question)
                .filter_by(question_id=question_id, class_id=class_id)
                .first()
            )
            if question_to_update:
                question_to_update.is_active = is_active
                session.commit()
                return (
                    jsonify({"success": True, "message": "Question status updated."}),
                    200,
                )
            else:
                return (
                    jsonify({"success": False, "message": "Question not found."}),
                    404,
                )
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route(
    "/class/<string:class_id>/question/<string:question_id>/edit", methods=["POST"]
)
def edit_question(class_id, question_id):
    data = request.get_json()
    db = SessionLocal()
    try:
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        if question:
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


@app.route(
    "/class/<string:class_id>/question/<string:question_id>/delete", methods=["DELETE"]
)
def delete_question(class_id, question_id):
    db = SessionLocal()
    try:
        question = (
            db.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        if question:
            if question.is_active:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Question is active. Please deactivate the question before deleting.",
                        }
                    ),
                    400,
                )
            db.delete(question)
            db.commit()
            return jsonify(
                {"success": True, "message": "Question deleted successfully."}
            )
        else:
            return jsonify({"success": False, "message": "Question not found."}), 404
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
