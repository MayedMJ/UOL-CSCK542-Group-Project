"""Five SQL reports for the university database.

Each function accepts an open sqlite3.Connection with foreign keys enabled.
The caller owns and closes the connection. These functions close their
cursors and leave database errors for the caller to handle.

With the default row factory, results are lists of tuples. A custom row
factory is preserved. No matches return an empty list; SQL NULL is None.
"""


import sqlite3

def query_students_by_lecturer(cursor, lecturer_id, course_id):
    cursor.execute("""
        SELECT s.name
        FROM Student s
        JOIN Registration r ON s.studentID = r.studentID
        JOIN CourseOffering co ON r.offeringID = co.offeringID
        WHERE co.courseID = ? AND co.lecturerID = ?
    """, (course_id, lecturer_id))
    return cursor.fetchall()

def query_final_year_students(cursor):
    cursor.execute("""
        SELECT name
        FROM Student
        WHERE year = 'Final' AND averageMark > 70
    """)
    return cursor.fetchall()

def query_unregistered_students(cursor, year, semester):
    cursor.execute("""
        SELECT s.name
        FROM Student s
        WHERE NOT EXISTS (
            SELECT 1
            FROM Registration r
            WHERE r.studentID = s.studentID
            AND r.academicYear = ?
            AND r.semester = ?
        )
    """, (year, semester))
    return cursor.fetchall()

def query_student_advisor(cursor, student_id):
    cursor.execute("""
        SELECT a.name
        FROM Advisor a
        JOIN Student s ON a.advisorID = s.advisorID
        WHERE s.studentID = ?
    """, (student_id,))
    return cursor.fetchall()

def query_department_staff(cursor, dept_id):
    cursor.execute("""
        SELECT name
        FROM Staff
        WHERE departmentID = ?
    """, (dept_id,))
    return cursor.fetchall()


# Dispatcher function expected by main.py
def run_query(cursor, choice, **kwargs):
    if choice == "1":
        return query_students_by_lecturer(cursor, kwargs.get("lecturer_id"), kwargs.get("course_id"))
    elif choice == "2":
        return query_final_year_students(cursor)
    elif choice == "3":
        return query_unregistered_students(cursor, kwargs.get("year"), kwargs.get("semester"))
    elif choice == "4":
        return query_student_advisor(cursor, kwargs.get("student_id"))
    elif choice == "5":
        return query_department_staff(cursor, kwargs.get("dept_id"))
    else:
        return []
