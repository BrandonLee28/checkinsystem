import sqlite3
import random

def generate_random_student_id():
    # Generates a random 8-character student ID
    return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))

def get_common_names():
    # Returns a list of common names
    return ["John", "Emma", "Michael", "Olivia", "William", "Sophia", "James", "Ava", "Benjamin", "Isabella"]

def create_database():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    # Create the students table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        student_id TEXT,
        name TEXT NOT NULL,
        check_in_time DATETIME,
        check_out_time DATETIME,
        checkedin BOOLEAN,
        role TEXT,
        reason TEXT)''')

    # Generate and insert random student records
    common_names = get_common_names()
    for _ in range(10):
        student_id = generate_random_student_id()
        name = random.choice(common_names)
        cursor.execute('''INSERT INTO students (student_id, name) 
                          VALUES (?, ?)''', (student_id, name))

    connection.commit()
    connection.close()

def print_all_data():
    connection = sqlite3.connect("students.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    connection.close()

# Create the database and insert 10 student records

"""create_database()
connection = sqlite3.connect("students.db")
cursor = connection.cursor()
cursor.execute('''INSERT INTO students (student_id, name,role) 
                          VALUES (?, ?,?)''', ('admin', 1234,'Admin'))
connection.commit()
connection.close()"""
print_all_data()
