from db import get_connection
from interface import menu, print_rows
from queries import (
    get_course_students,
    get_final_year_students,
    get_students_without_registrations,
    get_student_advisor,
    get_department_staff
)

def main():
    conn = get_connection()

    while True:
        choice = menu()

        if choice == "1":
            course = input("Enter course code (e.g., CS301): ")
            lecturer = int(input("Enter lecturer ID: "))
            rows = get_course_students(conn, course, lecturer)
            print_rows(rows)

        elif choice == "2":
            rows = get_final_year_students(conn)
            print_rows(rows)

        elif choice == "3":
            year = input("Enter academic year (e.g., 2026/27): ")
            semester = input("Enter semester (e.g., 1): ")
            rows = get_students_without_registrations(conn, year, semester)
            print_rows(rows)

        elif choice == "4":
            student_id = int(input("Enter student ID: "))
            rows = get_student_advisor(conn, student_id)
            print_rows(rows)

        elif choice == "5":
            dept_id = int(input("Enter department ID: "))
            rows = get_department_staff(conn, dept_id)
            print_rows(rows)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.\n")

    conn.close()

if __name__ == "__main__":
    main()
