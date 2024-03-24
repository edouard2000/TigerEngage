from flask import Flask, render_template

app = Flask(__name__)

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


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/student_dashboard")
def student_dashboard():
    student_name = "John Doe"
    return render_template(
        "student-dashboard.html", student_name=student_name, classes=classes
    )


@app.route("/class_dashboard/<int:class_id>")
def class_dashboard(class_id):
    class_info = next((c for c in classes if c["id"] == class_id), None)
    if class_info:
        class_name = class_info["name"]
    else:
        class_name = "Class not found"
    return render_template("class-dashboard.html", class_name=class_name)


if __name__ == "__main__":
    app.run(debug=True)
