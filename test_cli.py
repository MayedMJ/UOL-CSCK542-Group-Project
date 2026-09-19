"""Tests for the five menu options.

Each test uses a temporary database loaded from schema.sql and seed.sql.
SQLite 3.37 or later is required.
"""

from ast import literal_eval
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_DIR = Path(__file__).resolve().parent


class CliReportTests(unittest.TestCase):
    """Check each menu option against the seeded database."""

    def _assert_report(
        self, answers: list[str], expected_rows: list[tuple]
    ) -> None:
        """Enter the answers in order, then exit and compare report rows."""
        with TemporaryDirectory() as working_dir:
            database_path = Path(working_dir) / "university.db"
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                for filename in ("schema.sql", "seed.sql"):
                    connection.executescript(
                        (PROJECT_DIR / filename).read_text(encoding="utf-8")
                    )
                connection.commit()

            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PROJECT_DIR / "main.py"),
                    "--db",
                    str(database_path),
                ],
                input="\n".join(answers) + "\n0\n",
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=10,
            )

        self.assertEqual(
            result.returncode, 0, msg=result.stdout + result.stderr
        )
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Database error:", result.stdout)
        self.assertNotIn("Unexpected error:", result.stdout)
        self.assertIn("Exiting program...", result.stdout)
        self.assertIn("\nResults:\n", result.stdout)

        report = result.stdout.split("\nResults:\n", 1)[1].split("\n\n", 1)[0]
        rows = [literal_eval(line) for line in report.splitlines()]
        self.assertEqual(rows, expected_rows)

    def test_course_students_report(self) -> None:
        """CS301 with lecturer 1 returns the four enrolled students."""
        self._assert_report(
            ["1", "1", "CS301"],
            [
                (1, "Amina Yusuf"),
                (2, "Ben Carter"),
                (3, "Chloe Martin"),
                (4, "Daniel Okafor"),
            ],
        )

    def test_final_year_performance_report(self) -> None:
        """Only final-year students averaging above 70 are listed."""
        self._assert_report(
            ["2"],
            [(1, "Amina Yusuf", 75.0), (7, "George Evans", 80.0)],
        )

    def test_unregistered_students_report(self) -> None:
        """List students with no enrolments in semester 1 of 2026/27."""
        self._assert_report(
            ["3", "2026/27", "1"],
            [
                (6, "Farah Ali"),
                (8, "Hannah Reed"),
                (9, "Isaac Patel"),
                (10, "Jack Morgan"),
            ],
        )

    def test_student_advisor_report(self) -> None:
        """Student 1's result includes their advisor's email and phone."""
        self._assert_report(
            ["4", "1"],
            [(1, "Maya Patel", "maya.patel@example.test", "02079460001")],
        )

    def test_department_staff_report(self) -> None:
        """Department 1 includes academic and non-academic staff."""
        self._assert_report(
            ["5", "1"],
            [
                (1, "Maya Patel", "Academic"),
                (2, "Owen Reed", "Academic"),
                (1, "Noah Wilson", "Non-academic"),
                (2, "Priya Shah", "Non-academic"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
