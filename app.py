import flask
import auth

app = flask.Flask(__name__)
import os

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


students = [
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
    username = auth.authenticate()
    print(username)
    html_code = flask.render_template(
        "home.html",
        username=username,
    )
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


@app.route("/student_dashboard")
def student_dashboard():
    student_name = "John Doe"
    return flask.render_template(
        "student-dashboard.html", student_name=student_name, classes=classes
    )


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
    return flask.render_template("role-selection.html")


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
        "class-users.html", students=students, prof_name=prof_name
    )

@app.route("/professor_dashboard")
def professor_dashboard():
    prof_name = "Prof. John Doe" 
    return flask.render_template("professor-dashboard.html", prof_name=prof_name)



if __name__ == "__main__":
    app.run(debug=True)
