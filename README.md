# UOL-CSCK542-Group-Project  
A Python‑based university record management system developed for the CSCK542 Web Technology and Databases module.  
The system integrates SQLite as the backend database and provides a command‑line interface (CLI) for generating academic and administrative reports.

---

## Project Overview
This project demonstrates the design, implementation, and testing of a relational database system using SQLite, alongside a Python application that connects to the database and executes predefined SQL queries.

The system supports:
- Student registration reporting  
- Lecturer–course relationships  
- Advisor–student mapping  
- Department staff listings  
- Academic performance queries  

All functionality is accessible through a simple, menu‑driven CLI.

---

## Repository Structure

├── db.py              # Database connection module
├── interface.py       # CLI menu
├── main.py            # Application entry point
├── queries.py         # SQL query functions
├── schema.sql         # Database schema (tables, constraints)
├── seed.sql           # Sample data population
├── test_queries.py    # Unit tests (in-memory SQLite)
└── README.md          # Project documentation


---

## Database Setup
The project uses **SQLite 3.37+**.

**To create and populate the database:**

```bash
sqlite3 university.db ".read schema.sql"
sqlite3 university.db ".read seed.sql"

**Running the Application**

Ensure Python 3 is installed.

From the project directory, run: python main.py

You will see the CLI menu:
=== University Database Reports ===
1. Students in a course taught by a lecturer
2. Final-year students with average > 70%
3. Students without registrations
4. Student advisor details
5. Department staff
0. Exit

Running Tests
The project includes unit tests that use an in‑memory SQLite database (no external files required).

Run tests with: python3 -B -m unittest -v test_queries

Academic Context
This project was developed as part of the University of Liverpool MSc Computer Science module CSCK542, demonstrating:

Relational database design

SQL query development

Python–SQLite integration

Software engineering practices

Unit testing and validation


University of Liverpool — MSc Computer Science

