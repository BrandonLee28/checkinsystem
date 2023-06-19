from flask import Flask, render_template, redirect, url_for, request, flash, Response, send_file
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from student import StudentUserTerminal
import sqlite3
from excel import export_cursor_to_xlsx
import re
from dateutil import parser
from datetime import datetime, timedelta, date

from pytz import timezone





app = Flask(__name__)
app.secret_key = 'cancun'
login_manager = LoginManager(app)
login_manager.login_view = "signin"
current_day = None
tz = timezone('US/Eastern')



# User model
class User(UserMixin):
    def __init__(self, id,name,check_in_time,check_out_time,checkedin,checkedout,role, reason):
        self.id = id
        self.name = name
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.checkedin = checkedin
        self.checkedout = checkedout
        self.role = role
        self.reason = reason


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id = ?", (user_id,))
    user_data = cur.fetchone()


    if user_data is None:
        return None  # Return None if no user data is fouxnd
    id = user_data[1]
    name = user_data[2]
    check_in_time = user_data[3]
    check_out_time = user_data[4]
    checkedin = user_data[5]
    checkedout = user_data[6]
    role = user_data[7]
    reason = user_data[8]
    return User(id, name, check_in_time, check_out_time, checkedin, checkedout, role, reason)

@app.before_first_request
def set_current_day():
    global tz
    global current_day
    current_day = date.today()



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
        conn.close()
        if admin[2] == password:
            user_obj = User(admin[1],admin[2],admin[3],admin[4],admin[5],admin[6],admin[7],admin[8])
            login_user(user_obj)
            return redirect(url_for('admindashboard'))
        else:
            flash('Incorrect Password', 'error')
    return render_template('admin_login.html')

@app.route('/admindashboard', methods=['GET','POST'])
@login_required
def admindashboard():
    if request.method == "POST":
        if 'search_submit' in request.form:
            name = request.form['name']
            name = name.lower()
            name = name.capitalize()
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            query = f"SELECT * FROM students WHERE name LIKE '{name}%' AND student_id != 'admin'"
            cur.execute(query)
            students = cur.fetchall()
            return render_template('admin_dashboard.html', students=students)

        elif 'date_submit' in request.form:
            date = request.form['date']
            if not re.match(r"\d{4}-\d{2}-\d{2}", date):
                return redirect(url_for('admindashboard'))
            return redirect(f"/admindashboard/{date}")

    conn = sqlite3.connect('students.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id != 'admin' ORDER BY name ASC")
    students = cur.fetchall()
    if current_user.role == 'Admin':
        return render_template('admin_dashboard.html', students=students)
    else:
        return redirect(url_for('signin'))

def is_current_date(input_date):
    global tz
    current_date = date.today()
    current_date = str(current_date)
    input_date = str(input_date)
    return input_date == current_date

def duplicate_and_clear_table(db_file, original_table_name, duplicate_table_name, columns_to_clear):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Duplicate the table
    cursor.execute(f"CREATE TABLE {duplicate_table_name} AS SELECT * FROM {original_table_name}")

    # Remove data from specified columns in the original table
    for column in columns_to_clear:
        cursor.execute(f"UPDATE {original_table_name} SET {column} = NULL")

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()

@app.route("/admindashboard/<date>")
@login_required
def admintabledate(date):
    if current_user.role == 'Admin':
        if is_current_date(date):
            conn = sqlite3.connect('students.db')
            cur = conn.cursor()
            cur.execute("SELECT * FROM students WHERE student_id != 'admin' ORDER BY name ASC")
            students = cur.fetchall()
            if students == None:
                return redirect(url_for('admindashboard'))
            return render_template('admindate_dashboard.html', date=date, students=students)

        if not re.match(r"\d{4}-\d{2}-\d{2}", date) or len(str(date)) != 10:
            return redirect(url_for('admindashboard'))
        else:
            try:
                conn = sqlite3.connect('students.db')
                cur = conn.cursor()
                date_object = parser.parse(date).date()
                formatted_date = 'd' + date_object.strftime("%Y%m%d")
                cur.execute(f"SELECT * FROM {formatted_date} WHERE student_id != 'admin' ORDER BY name ASC")
                students = cur.fetchall()
                if students is None:
                    return redirect(url_for('admindashboard'))
                return render_template('admindate_dashboard.html', date=date, students=students)
            except sqlite3.OperationalError or parser.ParserError:
                return redirect(url_for('admindashboard'))


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
    global current_day
    today = date.today()
    if today > current_day:
        current_date = datetime.date.today()
        yesterday = current_date - datetime.timedelta(days=1)
        duplicate_table_name = 'd' + yesterday.strftime("%Y%m%d")
        # Perform your desired action here
        duplicate_and_clear_table('students.db', 'students', duplicate_table_name, ['check_in_time', 'check_out_time', 'checkedin','checkedout','reason'])
        current_day = today

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
            user_obj = User(user[1],user[2],user[3],user[4],user[5],user[6],user[7], user[8])
            login_user(user_obj)
            if 'checkin' in request.form:
                if terminal.is_checked_in(id):
                    flash('You are already checked in', 'error')
                else:
                    return redirect(url_for('checkin'))
            if 'checkout' in request.form:
                if terminal.is_checked_out(id):
                    flash('You are already checked out', 'error')
                else:
                    return redirect(url_for('checkout'))
            terminal.close()
    return render_template("signin.html")

@app.route('/logout')
@login_required
def logout():
    terminal = StudentUserTerminal("students.db")
    logout_user()
    return redirect(url_for('signin'))


if __name__ == '__main__':
    app.run(debug=True)