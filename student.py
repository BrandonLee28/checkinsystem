import sqlite3
from datetime import datetime

class StudentTerminal:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS students
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT NOT NULL,
                              reason TEXT,
                              check_in DATETIME,
                              check_out DATETIME)''')
        self.connection.commit()

    def check_in(self, student_name, reason):
        current_time = datetime.now()
        self.cursor.execute('''INSERT INTO students (name, reason, check_in) 
                               VALUES (?, ?, ?)''', (student_name, reason, current_time))
        self.connection.commit()
        print(f"{student_name} checked in at {current_time} with reason: {reason}.")

    def check_out(self, student_name, reason):
        current_time = datetime.now()
        self.cursor.execute('''UPDATE students SET check_out = ? 
                               WHERE name = ? AND check_out IS NULL''',
                            (current_time, student_name))
        if self.cursor.rowcount > 0:
            self.connection.commit()
            print(f"{student_name} checked out at {current_time} with reason: {reason}.")
        else:
            print(f"{student_name} has not checked in or already checked out.")

    def get_check_ins(self):
        self.cursor.execute("SELECT * FROM students WHERE check_out IS NULL")
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()

