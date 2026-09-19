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


if __name__ == "__main__":
    unittest.main()
