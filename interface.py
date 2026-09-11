from queries import (
    get_course_students,
    get_final_year_students,
    get_students_without_registrations,
    get_student_advisor,
    get_department_staff
)

def print_rows(rows):
    if not rows:
        print("\nNo results found.\n")
        return
    for row in rows:
        print(row)
    print()

def menu():
    print("\n=== University Database Reports ===")
    print("1. Students in a course taught by a lecturer")
    print("2. Final-year students with average > 70%")
    print("3. Students without registrations")
    print("4. Student advisor details")
    print("5. Department staff")
    print("0. Exit")
    return input("Choose an option: ")
