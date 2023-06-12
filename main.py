from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import cv2
from pyzbar import pyzbar
from student import StudentUserTerminal
import sqlite3

app = Flask(__name__)
app.secret_key = 'cancun'
login_manager = LoginManager(app)
login_manager.login_view = "signin"

# User model
class User(UserMixin):
    def __init__(self, id,name,check_in_time,check_out_time,checkedin,role, reason):
        self.id = id
        self.name = name
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.checkedin = checkedin
        self.role = role
@login_manager.user_loader
def load_user(user_id):
        # Here, you need to retrieve the user's information from the database based on the provided user_id
        # For simplicity, let's assume you have a function `get_user_by_id` that retrieves the user's information from the database
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (user_id,))
        user_data = cur.fetchone()  # Fetch the result of the query


        # Extract the necessary values from the user_data
        id = user_data[1]
        name = user_data[2]
        check_in_time = user_data[3]
        check_out_time = user_data[4]
        checkedin = user_data[5]
        role = user_data[6]
        reason = user_data[7]


        # Create and return the User object
        return User(id, name, check_in_time, check_out_time, checkedin, role, reason)

def generate_frames():
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break

        # Convert the frame to grayscale for barcode detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect barcodes in the grayscale frame
        barcodes = pyzbar.decode(gray)

        for barcode in barcodes:
            # Extract the barcode data and type
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type

            # Draw a rectangle around the detected barcode
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the barcode data as text on the frame
            cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Output the barcode data to the console
            print('Detected Barcode:', barcode_data)

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    if request.method == 'POST':
        terminal = StudentUserTerminal("students.db")

        reason = request.form.get('reason')

        terminal.check_in(current_user.id,reason)
        return redirect(url_for('logout'))
    return render_template("checkin.html", student=current_user)

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        terminal = StudentUserTerminal("students.db")
        reason = request.form.get('reason')
        terminal.check_out(current_user.id,reason)
        return redirect(url_for('logout'))
    return render_template("checkout.html", student=current_user)

@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE student_id = ?", (username,))
        admin = cur.fetchone()
        print(admin)
        conn.close()
        if admin[2] == password:
            user_obj = User(admin[1],admin[2],admin[3],admin[4],admin[5],admin[6],admin[7])
            login_user(user_obj)
            return redirect(url_for('admindashboard'))
        else:
            flash('Incorrect Password', 'error')
    return render_template('admin_login.html')

@app.route('/admindashboard', methods=['GET','POST'])
@login_required
def admindashboard():
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id != 'admin'")
    students = cur.fetchall()
    print(students[0][0])
    if current_user.role == 'Admin':
        return render_template('admin_dashboard.html', students=students)
    else:
        return redirect(url_for('signin'))




@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        if request.form['student_id'] == 'admin':
            return redirect(url_for('adminlogin'))
        terminal = StudentUserTerminal("students.db")
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        id = request.form['student_id']
        query = "SELECT * FROM students WHERE student_id = ?"
        cur.execute(query, (id,))
        user = cur.fetchone()
        conn.close()
        if user is not None:
            user_obj = User(user[1],user[2],user[3],user[4],user[5],user[6],user[7])
            login_user(user_obj)
            if 'checkin' in request.form:
                if terminal.is_checked_in(id):
                    flash('You are already checked in', 'error')
                else:
                    return redirect(url_for('checkin'))
            if 'checkout' in request.form:
                if terminal.is_checked_in(id):
                    return redirect(url_for('checkout'))
                else:
                    flash('You are already checked out', 'error')
            terminal.close()
    return render_template("signin.html")

@app.route('/logout')
@login_required
def logout():
    terminal = StudentUserTerminal("students.db")
    logout_user()
    return redirect(url_for('signin'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
