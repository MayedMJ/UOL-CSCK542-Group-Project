"""Run the university database reports from a command-line menu."""

import argparse
import sqlite3

from db import DEFAULT_DB_PATH, get_connection
from interface import get_academic_period, get_valid_id, show_menu
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
            choice = show_menu().strip()

            if choice == "0":
                print("Exiting program...")
                break

            if choice not in ("1", "2", "3", "4", "5"):
                print("Invalid choice. Please select an option from 0 to 5.")
                continue

            params = {}

            if choice == "1":
                params["lecturer_id"] = get_valid_id("Enter lecturer ID: ")
                params["course_id"] = input(
                    "Enter course code (e.g., CS301): "
                ).strip()

            elif choice == "2":
                pass  # no extra inputs

            elif choice == "3":
                year, semester = get_academic_period()
                if year is None or semester is None:
                    continue
                params["year"] = year
                params["semester"] = semester

            elif choice == "4":
                params["student_id"] = get_valid_id("Enter student ID: ")

            elif choice == "5":
                params["dept_id"] = get_valid_id("Enter department ID: ")

            try:
                results = run_query(cursor, choice, **params)
                print("\nResults:")
                if not results:
                    print("No results found.")
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
    parser = argparse.ArgumentParser(description="University database reports")
    parser.add_argument(
        "--db",
        metavar="PATH",
        default=DEFAULT_DB_PATH,
        help="database file (default: university.db beside this application)",
    )
    args = parser.parse_args()
    main(args.db)
