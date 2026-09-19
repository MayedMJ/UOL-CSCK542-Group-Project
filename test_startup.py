"""Check that main.py opens the menu and exits normally."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


PROJECT_DIR = Path(__file__).resolve().parent


class StartupTests(unittest.TestCase):
    """Run the application in a temporary directory."""

    def test_application_starts_and_exits(self) -> None:
        """Display the menu and close the application with option 0."""
        with TemporaryDirectory() as working_dir:
            database_path = Path(working_dir) / "university.db"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PROJECT_DIR / "main.py"),
                    "--db",
                    str(database_path),
                ],
                input="0\n",
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=10,
            )

        self.assertEqual(
            result.returncode, 0, msg=result.stdout + result.stderr
        )
        self.assertIn("University Database Reports", result.stdout)
        self.assertIn("Exiting program...", result.stdout)


if __name__ == "__main__":
    unittest.main()
