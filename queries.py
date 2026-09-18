"""
Five SQL reports for the university database.

Each function accepts an open sqlite3.Connection with foreign keys enabled.
The caller owns and closes the connection. These functions close their
cursors and leave database errors for the caller to handle.

With the default row factory, results are lists of tuples. A custom row
factory is preserved. No matches return an empty list; SQL NULL is None.
"""

import sqlite3

# 1. Students taught by a lecturer for a course
def query_students_by_lecturer(cursor, lecturer_id, course_id):
    cursor.execute("""
        SELECT s.name
        FROM Student s
        JOIN Registration r ON s.student_id = r.student_id
        JOIN CourseOffering co ON r.offering_id = co.offering_id
        WHERE co.course_id = ? AND co.lecturer_id = ?
    """, (course_id, lecturer_id))
    return cursor.fetchall()


# 2. Final‑year students with average mark > 70
def query_final_year_students(cursor):
    cursor.execute("""
        SELECT s.name, AVG(r.mark) AS averageMark
        FROM Student s
        JOIN Registration r ON s.student_id = r.student_id
        WHERE s.study_year = 4 AND s.graduation_status = 'Final'
        GROUP BY s.student_id
        HAVING AVG(r.mark) > 70
    """)
    return cursor.fetchall()


# 3. Students not registered in a given year/semester
def query_unregistered_students(cursor, year, semester):
    cursor.execute("""
        SELECT s.name
        FROM Student s
        WHERE NOT EXISTS (
            SELECT 1
            FROM Registration r
            WHERE r.student_id = s.student_id
              AND r.academic_year = ?
              AND r.semester = ?
        )
    """, (year, semester))
    return cursor.fetchall()


# 4. Student’s advisor
def query_student_advisor(cursor, student_id):
    cursor.execute("""
        SELECT a.name
        FROM Advisor a
        JOIN Student s ON a.advisor_id = s.advisor_id
        WHERE s.student_id = ?
    """, (student_id,))
    return cursor.fetchall()


# 5. Staff in a department
def query_department_staff(cursor, dept_id):
    cursor.execute("""
        SELECT name
        FROM Staff
        WHERE department_id = ?
    """, (dept_id,))
    return cursor.fetchall()


# Dispatcher function expected by main.py
def run_query(cursor, choice, **kwargs):
    if choice == "1":
        return query_students_by_lecturer(
            cursor,
            kwargs.get("lecturer_id"),
            kwargs.get("course_id"),
        )
    elif choice == "2":
        return query_final_year_students(cursor)
    elif choice == "3":
        return query_unregistered_students(
            cursor,
            kwargs.get("year"),
            kwargs.get("semester"),
        )
    elif choice == "4":
        return query_student_advisor(cursor, kwargs.get("student_id"))
    elif choice == "5":
        return query_department_staff(cursor, kwargs.get("dept_id"))
    else:
        return []
