"""Exercise database selection, input validation and empty CLI reports.

Run a copy of the application with temporary databases loaded from
schema.sql and seed.sql. Each test removes its files even if it fails.
The subprocess uses the same Python interpreter as the test runner.
"""

from ast import literal_eval
from contextlib import closing
from pathlib import Path
from shutil import copyfile
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import Optional
import unittest


PROJECT_DIR = Path(__file__).resolve().parent


class CliUsabilityTests(unittest.TestCase):
    """Check report behaviour through the application's entry point."""

    def setUp(self) -> None:
        """Copy the app and seed a temporary database for each test.

        Keeping the application copy beside its database allows location
        tests to run safely before and after the default path is fixed.
        No test opens the database in the repository.
        """
        temporary_dir = TemporaryDirectory()
        self.addCleanup(temporary_dir.cleanup)
        self.root = Path(temporary_dir.name)
        self.application_dir = self.root / "application"
        self.application_dir.mkdir()
        for filename in ("main.py", "db.py", "interface.py", "queries.py"):
            copyfile(PROJECT_DIR / filename, self.application_dir / filename)
        self._create_database(self.application_dir / "university.db")

    def _create_database(
        self, path: Path, advisor_name: str = "Maya Patel"
    ) -> None:
        """Seed a database, optionally changing a name to identify it.

        Distinct advisor names reveal which database the application
        opened without inspecting its connection code.
        """
        with closing(sqlite3.connect(path)) as connection:
            for filename in ("schema.sql", "seed.sql"):
                connection.executescript(
                    (PROJECT_DIR / filename).read_text(encoding="utf-8")
                )
            connection.execute(
                "UPDATE Lecturer SET name = ? WHERE lecturer_id = 1",
                (advisor_name,),
            )
            connection.commit()

    def _run_application(
        self,
        answers: list[str],
        working_dir: Optional[Path] = None,
        database_path: Optional[Path] = None,
    ) -> str:
        """Enter the supplied answers, exit and check for CLI errors.

        Launch beside the copied app unless another working directory is
        supplied. An explicit database is selected with --db PATH.
        """
        command = [
            sys.executable,
            "-B",
            str(self.application_dir / "main.py"),
        ]
        if database_path is not None:
            command.extend(["--db", str(database_path)])
        result = subprocess.run(
            command,
            input="\n".join(answers + ["0"]) + "\n",
            capture_output=True,
            text=True,
            cwd=working_dir or self.application_dir,
            timeout=10,
        )
        self.assertEqual(
            result.returncode, 0, msg=result.stdout + result.stderr
        )
        self.assertEqual(result.stderr, "")
        for message in (
            "Database error:",
            "Unexpected error:",
            "Failed to connect to the database:",
        ):
            self.assertNotIn(message, result.stdout)
        self.assertIn("Exiting program...", result.stdout)
        self.assertIn("Database connection closed.", result.stdout)
        return result.stdout

    def _assert_report(self, output: str, expected_rows: list[tuple]) -> None:
        """Require exactly one report and compare every returned row."""
        self.assertEqual(output.count("\nResults:\n"), 1)
        rows = [
            literal_eval(line)
            for line in output.splitlines()
            if line.startswith("(")
        ]
        self.assertEqual(rows, expected_rows)

    def test_default_database_from_another_directory(self) -> None:
        """Read the app's database from a different working directory.

        The launch folder must remain free of accidental database files.
        """
        working_dir = self.root / "other folder"
        working_dir.mkdir()

        output = self._run_application(["4", "1"], working_dir=working_dir)

        self._assert_report(
            output,
            [(1, "Maya Patel", "maya.patel@example.test", "02079460001")],
        )
        self.assertFalse((working_dir / "university.db").exists())

    def test_default_database_ignores_unrelated_database(self) -> None:
        """Ignore a different database found in the launch folder."""
        working_dir = self.root / "other folder"
        working_dir.mkdir()
        self._create_database(
            working_dir / "university.db", advisor_name="Unrelated advisor"
        )

        output = self._run_application(["4", "1"], working_dir=working_dir)

        self._assert_report(
            output,
            [(1, "Maya Patel", "maya.patel@example.test", "02079460001")],
        )

    def test_database_option_overrides_default(self) -> None:
        """Use --db to select a database whose path contains spaces."""
        database_path = self.root / "selected database.sqlite3"
        self._create_database(database_path, advisor_name="Selected advisor")

        output = self._run_application(
            ["4", "1"], database_path=database_path
        )

        self._assert_report(
            output,
            [
                (1, "Selected advisor",
                 "maya.patel@example.test", "02079460001"),
            ],
        )

    def test_blank_year_is_rejected(self) -> None:
        """Reject empty or whitespace-only years before reporting."""
        for year in ("", " \t "):
            with self.subTest(year=year):
                output = self._run_application(["3", year, "1"])

                self.assertNotIn("\nResults:\n", output)
                self.assertIn("cannot be blank", output)
                self.assertIn("Academic year", output)

    def test_blank_semester_is_rejected(self) -> None:
        """Reject empty or whitespace-only semesters before querying."""
        for semester in ("", " \t "):
            with self.subTest(semester=semester):
                output = self._run_application(["3", "2026/27", semester])

                self.assertNotIn("\nResults:\n", output)
                self.assertIn("cannot be blank", output)
                self.assertIn("semester", output)

    def test_blank_academic_period_is_rejected(self) -> None:
        """Reject both blank fields without listing any students."""
        output = self._run_application(["3", "", ""])

        self.assertNotIn("\nResults:\n", output)
        self.assertIn("cannot be blank", output)

    def test_academic_period_whitespace_is_trimmed(self) -> None:
        """Trim whitespace around a valid academic year and semester."""
        output = self._run_application(["3", " 2026/27 ", " 1 "])

        self._assert_report(
            output,
            [
                (6, "Farah Ali"),
                (8, "Hannah Reed"),
                (9, "Isaac Patel"),
                (10, "Jack Morgan"),
            ],
        )

    def test_invalid_menu_choice_is_rejected(self) -> None:
        """Explain invalid menu choices without producing a report."""
        for choice in ("", " \t ", "x", "6"):
            with self.subTest(choice=choice):
                output = self._run_application([choice])

                self.assertNotIn("\nResults:\n", output)
                self.assertRegex(output.lower(), r"invalid[^\n]*choice")

    def test_invalid_lecturer_id_can_be_corrected(self) -> None:
        """Retry invalid lecturer IDs before reporting on CS301."""
        for lecturer_id in ("", " \t ", "abc", "1.5"):
            with self.subTest(lecturer_id=lecturer_id):
                output = self._run_application(
                    ["1", lecturer_id, "1", "CS301"]
                )

                self.assertIn("numeric", output)
                self._assert_report(
                    output,
                    [
                        (1, "Amina Yusuf"),
                        (2, "Ben Carter"),
                        (3, "Chloe Martin"),
                        (4, "Daniel Okafor"),
                    ],
                )

    def test_invalid_student_id_can_be_corrected(self) -> None:
        """Retry invalid IDs before showing student 2's advisor."""
        for student_id in ("", " \t ", "abc", "1.5"):
            with self.subTest(student_id=student_id):
                output = self._run_application(["4", student_id, "2"])

                self.assertIn("numeric", output)
                self._assert_report(
                    output,
                    [
                        (1, "Maya Patel",
                         "maya.patel@example.test", "02079460001"),
                    ],
                )

    def test_invalid_department_id_can_be_corrected(self) -> None:
        """Retry invalid department IDs, then show department 2 once."""
        for department_id in ("", " \t ", "abc", "1.5"):
            with self.subTest(department_id=department_id):
                output = self._run_application(["5", department_id, "2"])

                self.assertIn("numeric", output)
                self._assert_report(
                    output,
                    [
                        (3, "Sofia Grant", "Academic"),
                        (3, "Liam Brooks", "Non-academic"),
                    ],
                )


if __name__ == "__main__":
    unittest.main()
