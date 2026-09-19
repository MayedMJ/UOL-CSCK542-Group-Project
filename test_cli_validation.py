"""Check database lookup and menu input handling."""

from contextlib import closing
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_DIR = Path(__file__).resolve().parent


class CliValidationTests(unittest.TestCase):
    """Run the real CLI against an isolated seeded database."""

    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.project = self.root / "project"
        self.project.mkdir()
        for filename in ("main.py", "db.py", "interface.py", "queries.py"):
            shutil.copyfile(PROJECT_DIR / filename, self.project / filename)
        with closing(sqlite3.connect(self.project / "university.db")) as conn:
            for filename in ("schema.sql", "seed.sql"):
                conn.executescript(
                    (PROJECT_DIR / filename).read_text(encoding="utf-8")
                )

    def run_app(self, answers, working_dir=None):
        result = subprocess.run(
            [sys.executable, "-B", str(self.project / "main.py")],
            input="\n".join(answers + ["0"]) + "\n",
            cwd=working_dir or self.project,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertNotIn("Database error:", result.stdout)
        self.assertNotIn("Unexpected error:", result.stdout)
        return result.stdout

    def test_report_from_another_folder(self):
        output = self.run_app(["2"], working_dir=self.root)
        self.assertIn("Amina Yusuf", output)
        self.assertFalse((self.root / "university.db").exists())

    def test_invalid_menu_option(self):
        output = self.run_app(["9"])
        self.assertIn("Invalid option", output)
        self.assertNotIn("Results:", output)

    def test_blank_academic_period(self):
        for period in (["", "1"], ["2026/27", ""], [" ", " "]):
            with self.subTest(period=period):
                output = self.run_app(["3"] + period)
                self.assertIn("cannot be blank", output)
                self.assertNotIn("Results:", output)

    def test_invalid_student_id_then_valid_id(self):
        output = self.run_app(["4", "", "abc", "1"])
        self.assertIn("ID cannot be blank", output)
        self.assertIn("Invalid input", output)
        self.assertIn("Maya Patel", output)

    def test_blank_course_code(self):
        output = self.run_app(["1", "1", " "])
        self.assertIn("Course code cannot be blank", output)
        self.assertNotIn("Results:", output)

    def test_no_results(self):
        output = self.run_app(["4", "999"])
        self.assertIn("No results found.", output)


if __name__ == "__main__":
    unittest.main()
