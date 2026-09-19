def show_menu():
    print("\n=== University Database Reports ===")
    print("1. List students taught by a lecturer for a course")
    print("2. List final-year students with average mark > 70")
    print("3. List students not registered in a given year/semester")
    print("4. Show a student's advisor")
    print("5. List staff in a department")
    print("0. Exit")
    return input("Enter your choice: ").strip()


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
