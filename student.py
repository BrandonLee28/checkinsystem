import sqlite3
from datetime import datetime

class StudentUserTerminal:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            student_id TEXT,
            name TEXT NOT NULL,
            check_in_time DATETIME,
            check_out_time DATETIME,
            checkedin BOOLEAN,
            checkedout BOOLEAN)''')
        self.connection.commit()

    def check_in(self, student_id,reason):
        current_time = datetime.now()
        self.cursor.execute('''UPDATE students SET check_in_time = ?, checkedin = 1, checkedout = 0, reason = ?
                               WHERE student_id = ?''', (current_time, reason, student_id))
        if self.cursor.rowcount > 0:
            self.connection.commit()
            print(f"Student with ID {student_id} checked in at {current_time}.")
        else:
            print(f"Student with ID {student_id} does not exist.")

    def check_out(self, student_id, reason):
        current_time = datetime.now()
        self.cursor.execute('''UPDATE students SET check_out_time = ?, checkedin = 0, checkedout = 1, reason = ? WHERE student_id = ? AND  checkedin = 1''',(current_time, reason, student_id))
        if self.cursor.rowcount > 0:
            self.connection.commit()
            print(f"Student with ID {student_id} checked out at {current_time}.")
        else:
            print(f"Student with ID {student_id} is already checked out or does not exist.")

    def get_check_ins(self):
        self.cursor.execute("SELECT * FROM students WHERE checkedin = 1")
        return self.cursor.fetchall()

    def is_checked_in(self, student_id):
        self.cursor.execute("SELECT checkedin FROM students WHERE student_id = ?", (student_id,))
        result = self.cursor.fetchone()
        if result:
            checked_in = result[0]
            if checked_in:
                return True
            return False

    def close(self):
        self.connection.close()


