import flask
import auth
from database import Base, User
import uuid  # Import the uuid module to generate unique IDs
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

app = flask.Flask(__name__)
import os

app.secret_key = os.environ["APP_SECRET_KEY"]

app.secret_key = os.environ["APP_SECRET_KEY"]
app.config["DATABASE_URL"] = 'postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage'
_DATABASE_URL = app.config["DATABASE_URL"]
_DATABASE_URL = _DATABASE_URL.replace('postgres://', 'postgresql://')

# Create engine and bind it to Base
_engine = create_engine(_DATABASE_URL)
Base.metadata.bind = _engine

# Create a sessionmaker to interact with the database
Session = sessionmaker(bind=_engine)
session = Session()

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


@app.route("/userlist")
def userlist():
    prof_name = "Prof. John Doe"
    return flask.render_template(
        "class-users.html", students=student, prof_name=prof_name
    )


@app.route("/professor_dashboard")
def professor_dashboard():
    prof_name = "Prof. John Doe"
    return flask.render_template("professor-dashboard.html", prof_name=prof_name)


@app.route("/add-question")
def add_question():
    return flask.render_template("add-question.html")


@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    stud = next((s for s in student if s["id"] == student_id), None)

    if stud is None:

        flask.flash("Student not found.", "error")
        return flask.redirect(flask.url_for("userlist"))

    if flask.request.method == "POST":
        stud["name"] = flask.request.form.get("name", "")
        stud["score"] = int(flask.request.form.get("score", 0))

        flask.flash("Student information updated successfully.", "success")
        return flask.redirect(flask.url_for("userlist"))
    return flask.render_template("edit_student.html", student=stud)


@app.route("/delete_student/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    global student
    student = [s for s in student if s["id"] != student_id]
    flask.flash("Student successfully deleted", "success")
    return flask.redirect(flask.url_for("userlist"))


if __name__ == "__main__":
    app.run(debug=True)
