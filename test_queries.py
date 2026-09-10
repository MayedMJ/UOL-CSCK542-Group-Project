"""Database integration tests for the five university reports.

Run from the project directory: python -B -m unittest -v test_queries
Requires Python with SQLite 3.37 or later for the saved STRICT schema.
Each test uses an independent in-memory database; university.db is not used.
"""

from pathlib import Path
import sqlite3
import unittest

import queries


PROJECT_DIR = Path(__file__).resolve().parent


class QueryTests(unittest.TestCase):
    """Compare report results with independently specified seed answers."""

    def setUp(self):
        """Recreate the schema and dummy data for each test."""
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        self.connection.execute("PRAGMA foreign_keys = ON")
        for filename in ("schema.sql", "seed.sql"):
            self.connection.executescript(
                (PROJECT_DIR / filename).read_text(encoding="utf-8")
            )

    def test_course_students_match_the_teaching_delivery(self):
        # Farah's historical CS301 delivery is not taught by Maya.
        self.assertEqual(
            queries.get_course_students(self.connection, "CS301", 1),
            [
                (1, "Amina Yusuf"),
                (2, "Ben Carter"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
            ],
        )

    def test_course_students_include_all_matching_periods(self):
        self.assertEqual(
            queries.get_course_students(self.connection, "CS301", 2),
            [
                (1, "Amina Yusuf"),
                (2, "Ben Carter"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
                (6, "Farah Ali"),
            ],
        )

    def test_course_students_are_distinct_across_deliveries(self):
        # This extra scenario changes only the test's in-memory database.
        self.connection.execute("INSERT INTO Enrolment VALUES (1, 8, 80)")
        self.assertEqual(
            queries.get_course_students(self.connection, "CS301", 2),
            [
                (1, "Amina Yusuf"),
                (2, "Ben Carter"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
                (6, "Farah Ali"),
            ],
        )

    def test_different_students_can_share_a_name(self):
        self.connection.execute(
            "UPDATE Student SET name = 'Amina Yusuf' WHERE student_id = 2"
        )
        self.assertEqual(
            queries.get_course_students(self.connection, "CS301", 1),
            [
                (1, "Amina Yusuf"),
                (2, "Amina Yusuf"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
            ],
        )

    def test_final_year_performance(self):
        # Amina: (80 + 70) / 2 = 75; George: (60 + 100) / 2 = 80.
        # Ben's exact 70, Ella's earlier study year, and missing grades
        # must not qualify. NULL enrolments must not reduce the averages.
        self.assertEqual(
            queries.get_final_year_students(self.connection),
            [(1, "Amina Yusuf", 75.0), (7, "George Evans", 80.0)],
        )

    def test_average_is_not_weighted_by_course_credits(self):
        self.connection.execute(
            "UPDATE Course SET credits = 30 WHERE course_code = 'CS101'"
        )
        self.assertEqual(
            queries.get_final_year_students(self.connection),
            [(1, "Amina Yusuf", 75.0), (7, "George Evans", 80.0)],
        )

    def test_students_without_current_registrations(self):
        # Historical and future registrations do not count. Hannah's
        # graduation status does not exclude her under the saved rules.
        self.assertEqual(
            queries.get_students_without_registrations(
                self.connection, "2026/27", "1"
            ),
            [
                (6, "Farah Ali"),
                (8, "Hannah Reed"),
                (9, "Isaac Patel"),
                (10, "Jack Morgan"),
            ],
        )

    def test_registration_report_uses_the_supplied_semester(self):
        # Isaac alone has a registration in 2026/27 semester 2.
        self.assertEqual(
            queries.get_students_without_registrations(
                self.connection, "2026/27", "2"
            ),
            [
                (1, "Amina Yusuf"),
                (2, "Ben Carter"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
                (5, "Ella Chen"),
                (6, "Farah Ali"),
                (7, "George Evans"),
                (8, "Hannah Reed"),
                (10, "Jack Morgan"),
            ],
        )

    def test_advisor_contact_details(self):
        self.assertEqual(
            queries.get_student_advisor(self.connection, 1),
            [(1, "Maya Patel", "maya.patel@example.test", "02079460001")],
        )

    def test_advisor_with_unrecorded_phone(self):
        self.assertEqual(
            queries.get_student_advisor(self.connection, 3),
            [(2, "Owen Reed", "owen.reed@example.test", None)],
        )

    def test_department_staff_include_both_categories(self):
        self.assertEqual(
            queries.get_department_staff(self.connection, 1),
            [
                (1, "Maya Patel", "Academic"),
                (2, "Owen Reed", "Academic"),
                (1, "Noah Wilson", "Non-academic"),
                (2, "Priya Shah", "Non-academic"),
            ],
        )

    def test_department_staff_filter_a_different_department(self):
        self.assertEqual(
            queries.get_department_staff(self.connection, 2),
            [
                (3, "Sofia Grant", "Academic"),
                (3, "Liam Brooks", "Non-academic"),
            ],
        )

    def test_unknown_filters_return_no_matches(self):
        cases = [
            (queries.get_course_students, ("UNKNOWN", 1)),
            (queries.get_course_students, ("CS301", 3)),
            (queries.get_student_advisor, (999,)),
            (queries.get_department_staff, (999,)),
        ]
        for function, arguments in cases:
            with self.subTest(report=function.__name__, arguments=arguments):
                self.assertEqual(function(self.connection, *arguments), [])

    def test_sql_like_input_is_treated_as_data(self):
        cases = [
            (queries.get_course_students, ("CS301' OR 1=1 --", 1)),
            (queries.get_student_advisor, ("3 OR 1=1",)),
            (queries.get_department_staff, ("1 OR 1=1",)),
        ]
        for function, arguments in cases:
            with self.subTest(report=function.__name__, arguments=arguments):
                self.assertEqual(function(self.connection, *arguments), [])

    def test_reports_on_an_empty_database(self):
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            (PROJECT_DIR / "schema.sql").read_text(encoding="utf-8")
        )
        cases = [
            (queries.get_course_students, ("CS301", 1)),
            (queries.get_final_year_students, ()),
            (
                queries.get_students_without_registrations,
                ("2026/27", "1"),
            ),
            (queries.get_student_advisor, (3,)),
            (queries.get_department_staff, (1,)),
        ]
        for function, arguments in cases:
            with self.subTest(report=function.__name__):
                self.assertEqual(function(connection, *arguments), [])

    def test_database_errors_are_not_reported_as_empty_results(self):
        self.connection.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            queries.get_student_advisor(self.connection, 1)


if __name__ == "__main__":
    unittest.main()
