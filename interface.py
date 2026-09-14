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

def run_query(cursor, choice):
    if choice == "1":
        lecturer = input("Enter lecturer name: ").strip()
        course = input("Enter course name: ").strip()
        cursor.execute("""
            SELECT s.name
            FROM Student s
            JOIN Registration r ON s.studentID = r.studentID
            JOIN Course c ON r.courseID = c.courseID
            JOIN Lecturer l ON c.lecturerID = l.lecturerID
            WHERE l.name = ? AND c.name = ?
        """, (lecturer, course))
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
        student = input("Enter student name: ").strip()
        cursor.execute("""
            SELECT a.name
            FROM Advisor a
            JOIN Student s ON a.advisorID = s.advisorID
            WHERE s.name = ?
        """, (student,))
        results = cursor.fetchall()
        print("Advisor details:", results)

    elif choice == "5":
        dept = input("Enter department name: ").strip()
        cursor.execute("""
            SELECT name
            FROM Staff
            WHERE department = ?
        """, (dept,))
        results = cursor.fetchall()
        print("Department staff:", results)
