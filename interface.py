"""Menu display and input helpers for the university reports CLI."""


def show_menu():
    """Display the reports menu and read the user's selection.

    Returns:
        str: The response as entered. The caller trims and validates it.
    """
    print("\n=== University Database Reports ===")
    print("1. List students taught by a lecturer for a course")
    print("2. List final-year students with average mark > 70")
    print("3. List students not registered in a given year/semester")
    print("4. Show a student's advisor")
    print("5. List staff in a department")
    print("0. Exit")
    return input("Enter your choice: ")


def get_academic_period():
    """Read an academic year and semester for the registration report.

    Trim surrounding whitespace from both responses. If either is blank,
    print an error so the caller can return to the menu.

    Returns:
        tuple: The year and semester as strings, or (None, None) when
            either response is blank.
    """
    year = input("Enter academic year (e.g., 2026/27): ").strip()
    semester = input("Enter semester (e.g., 1): ").strip()

    if not year or not semester:
        print("Error: Academic year and semester cannot be blank.")
        return None, None

    return year, semester


def get_valid_id(prompt):
    """Prompt until the user enters an integer ID.

    Strip surrounding whitespace from the response. Explain blank or
    non-integer input before prompting again.

    Args:
        prompt (str): Message displayed each time an ID is requested.

    Returns:
        int: The ID entered by the user.
    """
    while True:
        value = input(prompt).strip()
        if not value:
            print("Error: ID cannot be blank. Please enter a numeric value.")
            continue

        try:
            return int(value)
        except ValueError:
            print("Error: Invalid input. Please enter a numeric value.")
