"""Check foreign-key enforcement on the connection used by main.

Each test loads schema.sql and seed.sql into a real in-memory database.
Setup then disables foreign keys so the application must enable them.
Each test closes its database, including when an assertion fails.
"""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch

import main


PROJECT_DIR = Path(__file__).resolve().parent


class ApplicationConnectionTests(unittest.TestCase):
    """Check connection settings and enforcement during a report."""

    def setUp(self) -> None:
        """Load the seed data, then disable foreign-key enforcement."""
        self.connection = sqlite3.connect(":memory:")
        self.addCleanup(self.connection.close)
        for filename in ("schema.sql", "seed.sql"):
            self.connection.executescript(
                (PROJECT_DIR / filename).read_text(encoding="utf-8")
            )
        self.connection.commit()
        self.connection.execute("PRAGMA foreign_keys = OFF")

    def _run_application(self, query) -> None:
        """Run option 2 with the supplied query callback, then exit.

        The callback receives the application's cursor, menu choice
        and filters. Connections use this test's in-memory database.
        main configures and closes the connection.
        """
        output = StringIO()
        with (
            patch("main.sqlite3.connect", return_value=self.connection),
            patch("main.show_menu", side_effect=["2", "0"]),
            patch("main.run_query", side_effect=query) as report,
            redirect_stdout(output),
        ):
            main.main()

        report.assert_called_once()
        self.assertNotIn("Database error:", output.getvalue())
        self.assertNotIn("Unexpected error:", output.getvalue())

    def test_application_enables_foreign_keys(self) -> None:
        """Check that foreign keys are enabled when a report starts.

        Record the setting on the cursor passed by main. Assert it
        after main returns so its error handler cannot catch a failed
        assertion.
        """
        settings = []

        def read_setting(cursor, choice, **kwargs):
            settings.append(
                cursor.execute("PRAGMA foreign_keys").fetchone()[0]
            )
            return []

        self._run_application(read_setting)

        self.assertEqual(settings, [1])

    def test_application_rejects_enrolment_for_missing_student(self) -> None:
        """Reject an enrolment whose student does not exist.

        Delivery 1 exists in the seed data, but student 999 does not.
        Attempt the insert using the application's cursor. Roll it
        back before the report finishes, whether it succeeds or fails.
        """
        errors = []

        def insert_enrolment(cursor, choice, **kwargs):
            try:
                cursor.execute(
                    "INSERT INTO Enrolment (student_id, delivery_id) "
                    "VALUES (?, ?)",
                    (999, 1),
                )
            except sqlite3.IntegrityError as error:
                errors.append(str(error))
            finally:
                cursor.connection.rollback()
            return []

        self._run_application(insert_enrolment)

        self.assertEqual(errors, ["FOREIGN KEY constraint failed"])


if __name__ == "__main__":
    unittest.main()
