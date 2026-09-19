"""Run the university database reports from a command-line menu."""

import argparse
import sqlite3

from db import DEFAULT_DB_PATH, get_connection
from interface import show_menu
from queries import run_query


def main(db_path=DEFAULT_DB_PATH) -> None:
    """Run the report menu using the selected database.

    With no path supplied, use university.db beside this application.
    Explicit relative paths resolve from the current working directory.
    """
    conn = None
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()

        while True:
            choice = show_menu()

            if choice == "0":
                print("Exiting program...")
                break

            params = {}

            if choice == "1":
                params["lecturer_id"] = input("Enter lecturer ID: ")
                params["course_id"] = input("Enter course ID: ")

            elif choice == "2":
                pass  # no extra inputs

            elif choice == "3":
                params["year"] = input("Enter academic year (e.g., 2026/27): ")
                params["semester"] = input("Enter semester (e.g., 1): ")

            elif choice == "4":
                params["student_id"] = input("Enter student ID: ")

            elif choice == "5":
                params["dept_id"] = input("Enter department ID: ")

            try:
                results = run_query(cursor, choice, **params)
                print("\nResults:")
                for row in results:
                    print(row)
                print()

            except sqlite3.OperationalError as e:
                print("Database error:", e)
                print("Please ensure the database is set up correctly using schema.sql and seed.sql.")
            except Exception as e:
                print("Unexpected error:", e)

    except sqlite3.Error as e:
        print("Failed to connect to the database:", e)

    finally:
        if conn:
            conn.close()
            print("Database connection closed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="University database reports")
    parser.add_argument(
        "--db",
        metavar="PATH",
        default=DEFAULT_DB_PATH,
        help="database file (default: university.db beside this application)",
    )
    args = parser.parse_args()
    main(args.db)
