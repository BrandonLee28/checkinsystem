from flask import Flask, render_template, redirect, url_for, request, flash, Response, send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from student import StudentUserTerminal
import sqlite3
import time
from excel import export_cursor_to_xlsx

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



@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    if request.method == 'POST':
        terminal = StudentUserTerminal("students.db")

        reason = request.form.get('reason')

        terminal.check_in(current_user.id,reason)

        return render_template("checkinsplash.html"), {"Refresh": "2; url=/logout"}


    return render_template("checkin.html", student=current_user)

@app.route('/admindashboard/download', methods=['GET', 'POST'])
@login_required
def exceldownload():
    if current_user.role == 'Admin':
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id != 'admin' ORDER BY name ASC")

        # Export the cursor data to an Excel file
        excel_buffer = export_cursor_to_xlsx(cursor)

        cursor.close()
        conn.close()

        # Send the Excel file as a response for download
        return send_file(excel_buffer,download_name="output.xlsx")
    else:
        return redirect(url_for('signin'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        terminal = StudentUserTerminal("students.db")
        reason = request.form.get('reason')
        terminal.check_out(current_user.id,reason)
        return render_template("checkoutsplash.html"), {"Refresh": "2; url=/logout"}

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
    if request.method == "POST":
        name = request.form['name']
        name = name.lower()
        name = name.capitalize()
        conn = sqlite3.connect('students.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE name = ?" , (name,))
        students = cur.fetchall()
        return render_template('admin_dashboard.html', students=students)
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id != 'admin' ORDER BY name ASC")
    students = cur.fetchall()
    if current_user.role == 'Admin':
        return render_template('admin_dashboard.html', students=students)
    else:
        return redirect(url_for('signin'))

@app.route('/admindashboard/sort_by_<column>/<order>')
@login_required
def sort_students(column,order):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    query = f"SELECT * FROM students WHERE student_id != 'admin' ORDER BY {column} {order.upper()}"
    cur.execute(query)
    students = cur.fetchall()
    conn.close()
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
