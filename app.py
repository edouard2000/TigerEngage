from flask import Flask, render_template

app = Flask(__name__)

classes = [
    {
        "name": "Introduction to Python",
        "instructor": "Prof. John Doe",
        "is_active": True,
    },
    {
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


@app.route('/student_dashboard')
def student_dashboard():
    student_name = "John Doe" 
    return render_template('student-dashboard.html', student_name=student_name, classes=classes)



if __name__ == "__main__":
    app.run(debug=True)
