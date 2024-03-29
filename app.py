import os
import flask
from flask import request, flash, redirect, url_for, render_template
import auth

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


@app.route("/")
def home():

    html_code = flask.render_template("home.html")
    response = flask.make_response(html_code)
    return response


@app.route("/logoutapp", methods=["GET"])
def logoutapp():
    return auth.logoutapp()


@app.route("/logoutcas", methods=["GET"])
def logoutcas():
    return auth.logoutcas()


@app.route("/login")
def login():
    return flask.render_template("login.html")


@app.route("/register")
def register():
    return flask.render_template("register.html")

# Route to handle the form submission
@app.route('/register', methods=['POST'])
def process_registration():
    # Generate a unique user_id
    user_id = str(uuid.uuid4())

    # Fetch data from the form
    first_name = flask.request.form['firstName']
    last_name = flask.request.form['lastName']
    email = flask.request.form['email']
    password = flask.request.form['password']

    # Do something with the data (e.g., store it in a database)
    name = first_name + " " + last_name
    new_user = User(user_id=user_id, email=email, password_hash=password, role='student', name=name)
    session.add(new_user)

    try:
        # Attempt to commit the session
        session.commit()
        # If the registration is successful, redirect the user
        return flask.redirect(flask.url_for('new_student_dashboard', name=name))
    except IntegrityError as e:
        # Rollback the session to prevent further errors
        session.rollback()

        # Handle the unique constraint violation error
        error_message = "Email address already exists. Please choose a different email."
        # You can log the error or display a user-friendly message
        print(f"Error: {e}")
        return flask.render_template('denied.html', error_message=error_message)

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


@app.route("/feedback")
def feedback():
    feedback_data = {
        "question_content": "What is the capital of France?",
        "answers_summary": "Most students answered correctly that the capital of France is Paris.",
        "correct_answer": "The correct answer is Paris.",
        "user_answer": "Your answer was Paris.",
    }
    return flask.render_template("feedback.html", **feedback_data)


@app.route("/chat")
def chat():
    return flask.render_template("chat.html")


@app.route("/questions")
def questions():
    return flask.render_template("Question.html")


@app.route("/role-selection")
def role_selection():
    html_code = flask.render_template("role-selection.html")
    response = flask.make_response(html_code)
    return response


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


if __name__ == "__main__":
    app.run(debug=True)
