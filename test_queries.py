"""Database integration tests for the five university reports.

Run from the project directory: python3 -B -m unittest -v test_queries
Requires Python with SQLite 3.37 or later for the saved STRICT schema.
Each test uses its own in-memory database and closes it during cleanup.
The repository's university.db is not used.
"""

from pathlib import Path
import sqlite3
import unittest

import queries


PROJECT_DIR = Path(__file__).resolve().parent


class QueryTests(unittest.TestCase):
    """Compare report results with expected rows from the seed data.

    Expected rows are specified independently of the query functions.
    Each test starts with a fresh database, so changes stay local to it.
    """

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
        """Match enrolment and teaching on the same course delivery.

        Maya teaches the four students in the current CS301 delivery.
        Farah's historical CS301 delivery is taught by another lecturer,
        so she must not appear in Maya's report.
        """
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
        """Include students from every delivery taught by the lecturer.

        Owen teaches CS301 in both the current and historical periods.
        Farah must appear alongside the four current students.
        """
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
        """List a student once when several deliveries match the query.

        Enrol Amina in a second CS301 delivery taught by Owen. She must
        still appear once, with the other matching students retained.
        """
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
        """Keep both students when they share the same name.

        Give Ben the same name as Amina. Keep both students in ID order;
        a name does not identify a student.
        """
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
        """Apply the final-year rule and the strict average threshold.

        Amina averages (80 + 70) / 2 = 75. George averages 80 from
        60 and 100. Ben's exact 70, Ella's earlier study year and
        students with no recorded grades do not qualify. NULL grades
        must not reduce the averages.
        """
        self.assertEqual(
            queries.get_final_year_students(self.connection),
            [(1, "Amina Yusuf", 75.0), (7, "George Evans", 80.0)],
        )

    def test_average_is_not_weighted_by_course_credits(self):
        """Keep the average unchanged when course credits change.

        Increase CS101 to 30 credits. Amina and George must retain their
        unweighted averages of 75 and 80.
        """
        self.connection.execute(
            "UPDATE Course SET credits = 30 WHERE course_code = 'CS101'"
        )
        self.assertEqual(
            queries.get_final_year_students(self.connection),
            [(1, "Amina Yusuf", 75.0), (7, "George Evans", 80.0)],
        )

    def test_students_without_current_registrations(self):
        """Find students with no enrolments in semester 1 of 2026/27.

        Historical and future enrolments do not count for this period.
        Hannah must still appear because graduation status is not a
        filter in this report.
        """
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
        """Find missing enrolments using the requested semester.

        Isaac is the only student enrolled in semester 2 of 2026/27.
        Every other student must appear, including those in semester 1.
        """
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
        """Return the assigned advisor's identity and contact details.

        Student 1 is assigned to Maya. The row must contain her lecturer
        ID, name, email and phone in the documented order.
        """
        self.assertEqual(
            queries.get_student_advisor(self.connection, 1),
            [(1, "Maya Patel", "maya.patel@example.test", "02079460001")],
        )

    def test_advisor_with_unrecorded_phone(self):
        """Preserve an advisor whose phone number has not been recorded.

        Student 3 is assigned to Owen. His identity and email must still
        be returned, with None in the phone column.
        """
        self.assertEqual(
            queries.get_student_advisor(self.connection, 3),
            [(2, "Owen Reed", "owen.reed@example.test", None)],
        )

    def test_department_staff_include_both_categories(self):
        """Include lecturers and non-academic staff from department 1.

        IDs 1 and 2 occur in both staff tables. Retain all four people,
        ordered by category and then ID.
        """
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
        """Apply the department filter to both staff categories.

        Department 2 contains Sofia and Liam. Neither part of the query
        may include staff from department 1.
        """
        self.assertEqual(
            queries.get_department_staff(self.connection, 2),
            [
                (3, "Sofia Grant", "Academic"),
                (3, "Liam Brooks", "Non-academic"),
            ],
        )

    def test_unknown_filters_return_no_matches(self):
        """Return an empty list for filters with no matching rows.

        Cover an unknown course, a lecturer who does not teach CS301,
        and unknown student and department IDs.
        """
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
        """Treat SQL-like filter values as literal data.

        A quoted course value and OR expressions in student and
        department IDs must produce no matches, without broadening the
        query or causing a SQL error.
        """
        cases = [
            (queries.get_course_students, ("CS301' OR 1=1 --", 1)),
            (queries.get_student_advisor, ("3 OR 1=1",)),
            (queries.get_department_staff, ("1 OR 1=1",)),
        ]
        for function, arguments in cases:
            with self.subTest(report=function.__name__, arguments=arguments):
                self.assertEqual(function(self.connection, *arguments), [])

    def test_reports_on_an_empty_database(self):
        """Return an empty list from each report on an empty schema.

        Create a separate database without seed rows. Each report must
        execute successfully even though it has nothing to return.
        """
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
        """Raise a database error when the connection is closed.

        Close the connection before requesting an advisor. The query
        must raise ProgrammingError so the caller can distinguish the
        failure from a valid report with no matches.
        """
        self.connection.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            queries.get_student_advisor(self.connection, 1)


if __name__ == "__main__":
    unittest.main()
