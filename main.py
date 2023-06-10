from flask import Flask, render_template, Response
from student import StudentTerminal
import barcodescanner

app = Flask(__name__)

@app.route('/')
def index():
    terminal = StudentTerminal("students.db")
    
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)