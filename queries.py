"""Five SQL reports for the university database.

The get_* functions accept an open sqlite3.Connection. The run_query
dispatcher accepts a cursor and uses its connection to call them.
The caller owns and closes the connection and any supplied cursor.
The query functions close the cursors they create and leave database
errors for the caller to handle.

With the default row factory, results are lists of tuples. A custom row
factory is preserved. No matches return an empty list; SQL NULL is None.
"""


def get_course_students(connection, course_code, lecturer_id):
    """Return students enrolled in a course taught by a lecturer.

    Args:
        connection: Open SQLite connection, as described above.
        course_code: Course code as text, for example "CS301".
        lecturer_id: Integer lecturer ID.

    Returns:
        Rows containing (student_id, name), ordered by student_id.
        Enrolment and teaching must match the same delivery. All periods
        are included, and each student appears once.
    """
    sql = """
        SELECT DISTINCT s.student_id, s.name
        FROM Student AS s
        JOIN Enrolment AS e ON e.student_id = s.student_id
        JOIN CourseDelivery AS d ON d.delivery_id = e.delivery_id
        JOIN TeachingAssignment AS t ON t.delivery_id = d.delivery_id
        WHERE d.course_code = ?
          AND t.lecturer_id = ?
        ORDER BY s.student_id
    """
    cursor = connection.execute(sql, (course_code, lecturer_id))
    try:
        return cursor.fetchall()
    finally:
        cursor.close()


def get_final_year_students(connection):
    """Return final-year students with an average grade strictly above 70%.

    Args:
        connection: Open SQLite connection, as described above.

    Returns:
        Rows containing (student_id, name, average_grade), ordered by ID.
        Final year means study_year equals programme duration. The average
        is unweighted across recorded final grades; NULL grades are
        excluded. Students with no recorded grades do not qualify.
    """
    sql = """
        SELECT s.student_id, s.name, AVG(e.final_grade) AS average_grade
        FROM Student AS s
        JOIN Programme AS p ON p.programme_id = s.programme_id
        JOIN Enrolment AS e ON e.student_id = s.student_id
        WHERE s.study_year = p.duration_years
        GROUP BY s.student_id, s.name
        HAVING AVG(e.final_grade) > 70
        ORDER BY s.student_id
    """
    cursor = connection.execute(sql)
    try:
        return cursor.fetchall()
    finally:
        cursor.close()


def get_students_without_registrations(connection, academic_year, semester):
    """Return students without enrolments in the specified academic period.

    Args:
        connection: Open SQLite connection, as described above.
        academic_year: Academic year as text, for example "2026/27".
        semester: Semester as text, for example "1".

    Returns:
        Rows containing (student_id, name), ordered by student_id.
        The caller supplies the designated current period. Enrolments in
        other periods do not count. Graduation status is not a filter.
    """
    sql = """
        SELECT s.student_id, s.name
        FROM Student AS s
        WHERE NOT EXISTS (
            SELECT 1
            FROM Enrolment AS e
            JOIN CourseDelivery AS d ON d.delivery_id = e.delivery_id
            WHERE e.student_id = s.student_id
              AND d.academic_year = ?
              AND d.semester = ?
        )
        ORDER BY s.student_id
    """
    cursor = connection.execute(sql, (academic_year, semester))
    try:
        return cursor.fetchall()
    finally:
        cursor.close()


def get_student_advisor(connection, student_id):
    """Return the faculty advisor and contact details for a student.

    Args:
        connection: Open SQLite connection, as described above.
        student_id: Integer student ID.

    Returns:
        One row containing (lecturer_id, name, email, phone), or no rows
        if the student does not exist. An unrecorded phone number is None.
    """
    sql = """
        SELECT l.lecturer_id, l.name, l.email, l.phone
        FROM Student AS s
        JOIN Lecturer AS l ON l.lecturer_id = s.advisor_id
        WHERE s.student_id = ?
    """
    cursor = connection.execute(sql, (student_id,))
    try:
        return cursor.fetchall()
    finally:
        cursor.close()


def get_department_staff(connection, department_id):
    """Return academic and non-academic staff in a department.

    Args:
        connection: Open SQLite connection, as described above.
        department_id: Integer department ID.

    Returns:
        Rows containing (staff_id, name, staff_category), ordered by
        category and ID. Categories are "Academic" and "Non-academic".
        IDs belong to their category; different categories can share an ID.
    """
    sql = """
        SELECT lecturer_id AS staff_id, name, 'Academic' AS staff_category
        FROM Lecturer
        WHERE department_id = ?

        UNION ALL

        SELECT staff_id, name, 'Non-academic' AS staff_category
        FROM NonAcademicStaff
        WHERE department_id = ?

        ORDER BY staff_category, staff_id
    """
    cursor = connection.execute(sql, (department_id, department_id))
    try:
        return cursor.fetchall()
    finally:
        cursor.close()


def run_query(cursor, choice, **kwargs):
    """Run the report selected from the application menu.

    Args:
        cursor: Open SQLite cursor whose connection is used for the query.
        choice: Menu option as text, from "1" to "5".
        **kwargs: Filters entered through the CLI. Option "1" uses
            lecturer_id and course_id; "3" uses year and semester;
            "4" uses student_id; "5" uses dept_id. Option "2" needs none.
            The course_id value is a course code, such as "CS301".

    Returns:
        Rows from the selected get_* function, using its documented
        column order. An unknown menu option returns an empty list.

    Database errors propagate to the caller. The supplied cursor and
    its connection remain open.
    """
    connection = cursor.connection
    if choice == "1":
        return get_course_students(
            connection,
            kwargs.get("course_id"),
            kwargs.get("lecturer_id"),
        )
    elif choice == "2":
        return get_final_year_students(connection)
    elif choice == "3":
        return get_students_without_registrations(
            connection,
            kwargs.get("year"),
            kwargs.get("semester"),
        )
    elif choice == "4":
        return get_student_advisor(connection, kwargs.get("student_id"))
    elif choice == "5":
        return get_department_staff(connection, kwargs.get("dept_id"))
    else:
        return []
