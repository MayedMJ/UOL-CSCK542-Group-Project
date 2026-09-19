# University Database Reports

A Python command-line application for querying student enrolments, grades,
advisors and staff in a SQLite database.

## Requirements

- Python 3.9 or later, with SQLite 3.37 or later.
- The `sqlite3` command-line tool, version 3.37 or later, for database setup.

The application and tests use only the Python standard library.

Check the SQLite versions used by Python and the command-line tool:

```sh
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
sqlite3 --version
```

## Quick start

From the repository root, create a new database with the sample data and start
the application:

```sh
sqlite3 -bail university.db ".read schema.sql"
sqlite3 -bail university.db ".read seed.sql"
python3 main.py
```

Run the schema and seed commands once for each new database. They do not reset
an existing database.

## Usage

Choose a report from the menu. The examples below use the supplied sample data.

| Option | Report | Example input |
| --- | --- | --- |
| 1 | Students taught by a lecturer for a course | Lecturer `1`, course `CS301` |
| 2 | Final-year students with an average grade above 70% | None |
| 3 | Students without enrolments in an academic period | Year `2026/27`, semester `1` |
| 4 | A student's advisor and contact details | Student `1` |
| 5 | Academic and non-academic staff in a department | Department `1` |

Enter `0` to exit.

By default, the application opens `university.db` beside `main.py`, regardless
of the terminal's working directory. Pass an explicit database path with
`--db`:

```sh
python3 main.py --db university.db
```

The selected database must already contain the schema. Relative paths supplied
through `--db` resolve from the terminal's working directory.

Show the command-line options:

```sh
python3 main.py --help
```

## Tests

Run the full suite from the repository root:

```sh
python3 -B -m unittest discover -v
```

The suite covers query results, application startup, menu integration, database
selection, input validation, empty reports and foreign-key enforcement.

Tests use isolated in-memory and temporary databases. The repository’s
`university.db` is not accessed.
