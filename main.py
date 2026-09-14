import sqlite3
from interface import show_menu
from queries import run_query

def main():
    conn = None
    try:
        # Attempt to connect to the database
        conn = sqlite3.connect("university.db")
        cursor = conn.cursor()

        while True:
            choice = show_menu()
            if choice == "0":
                print("Exiting program...")
                break

            try:
                run_query(cursor, choice)
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
    main()
