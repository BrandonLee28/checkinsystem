from flask import Flask, render_template, Response
from student import StudentTerminal
import cv2

app = Flask(__name__)


@app.route('/dashboard')
def index():
    terminal = StudentTerminal("students.db")

    return render_template("dashboard.html")

@app.route('/')
def signin():

    return render_template("signin.html")

if __name__ == '__main__':
    app.run(debug=True)