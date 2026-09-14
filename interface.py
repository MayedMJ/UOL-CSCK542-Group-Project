import sqlite3

def show_menu():
    print("\n=== University Database Reports ===")
    print("1. Students in a course taught by a lecturer")
    print("2. Final-year students with average > 70%")
    print("3. Students without registrations")
    print("4. Student advisor details")
    print("5. Department staff")
    print("0. Exit")
    return input("Choose an option: ")

def get_academic_period():
    year = input("Enter academic year (e.g., 2026/27): ").strip()
    semester = input("Enter semester (e.g., 1): ").strip()

    if not year or not semester:
        print("Error: Academic year and semester cannot be blank.")
        return None, None

    return year, semester

def get_valid_id(prompt):
    while True:
        value = input(prompt).strip()
        if not value:
            print("Error: ID cannot be blank. Please enter a numeric value.")
            continue
        try:
            return int(value)
        except ValueError:
            print("Error: Invalid input. Please enter a numeric value.")

def run_query(cursor, choice):
    if choice == "1":
        lecturer_id = get_valid_id("Enter lecturer ID: ")
        course_id = get_valid_id("Enter course ID: ")
        cursor.execute("""
            SELECT s.name
            FROM Student s
            JOIN Registration r ON s.studentID = r.studentID
            JOIN CourseOffering co ON r.offeringID = co.offeringID
            WHERE co.courseID = ? AND co.lecturerID = ?
        """, (course_id, lecturer_id))
        results = cursor.fetchall()
        print("Results:", results)

    elif choice == "2":
        cursor.execute("""
            SELECT name
            FROM Student
            WHERE year = 'Final' AND averageMark > 70
        """)
        results = cursor.fetchall()
        print("Results:", results)

    elif choice == "3":
        year, semester = get_academic_period()
        if year and semester:
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
            results = cursor.fetchall()
            print("Unregistered students:", results)

    elif choice == "4":
        student_id = get_valid_id("Enter student ID: ")
        cursor.execute("""
            SELECT a.name
            FROM Advisor a
            JOIN Student s ON a.advisorID = s.advisorID
            WHERE s.studentID = ?
        """, (student_id,))
        results = cursor.fetchall()
        print("Advisor details:", results)

    elif choice == "5":
        dept_id = get_valid_id("Enter department ID: ")
        cursor.execute("""
            SELECT name
            FROM Staff
            WHERE departmentID = ?
        """, (dept_id,))
        results = cursor.fetchall()
        print("Department staff:", results)
