import sqlite3

from db import get_connection
from interface import get_academic_period, get_valid_id, show_menu
from queries import run_query


def main():
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        while True:
            choice = show_menu()

            if choice == "0":
                print("Exiting program...")
                break

            if choice not in {"1", "2", "3", "4", "5"}:
                print("Invalid option. Choose 0 to 5.")
                continue

            params = {}

            if choice == "1":
                params["lecturer_id"] = get_valid_id("Enter lecturer ID: ")
                params["course_id"] = input(
                    "Enter course code (e.g., CS301): "
                ).strip()
                if not params["course_id"]:
                    print("Course code cannot be blank.")
                    continue

            elif choice == "2":
                pass  # no extra inputs

            elif choice == "3":
                year, semester = get_academic_period()
                if year is None:
                    continue
                params["year"] = year
                params["semester"] = semester

            elif choice == "4":
                params["student_id"] = get_valid_id("Enter student ID: ")

            elif choice == "5":
                params["dept_id"] = get_valid_id("Enter department ID: ")

            try:
                results = run_query(cursor, choice, **params)
                if not results:
                    print("No results found.")
                    continue
                print("\nResults:")
                for row in results:
                    print(row)
                print()

            except sqlite3.OperationalError as e:
                print("Database error:", e)
                print(
                    "Please ensure the database is set up correctly "
                    "using schema.sql and seed.sql."
                )
            except Exception as e:
                print("Unexpected error:", e)

    except sqlite3.Error as e:
        print("Failed to connect to the database:", e)

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
