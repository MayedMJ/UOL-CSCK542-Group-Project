PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

CREATE TABLE Department (
    department_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    faculty TEXT NOT NULL CHECK (length(trim(faculty)) > 0)
) STRICT;

CREATE TABLE Programme (
    programme_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    degree_awarded TEXT NOT NULL CHECK (length(trim(degree_awarded)) > 0),
    duration_years INT NOT NULL CHECK (duration_years > 0)
) STRICT;

CREATE TABLE Lecturer (
    lecturer_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    email TEXT NOT NULL CHECK (length(trim(email)) > 0),
    phone TEXT CHECK (length(trim(phone)) > 0),
    department_id INT NOT NULL
        REFERENCES Department(department_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE NonAcademicStaff (
    staff_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    job_title TEXT NOT NULL CHECK (length(trim(job_title)) > 0),
    employment_type TEXT NOT NULL CHECK (length(trim(employment_type)) > 0),
    salary REAL CHECK (salary >= 0),
    department_id INT NOT NULL
        REFERENCES Department(department_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE Course (
    course_code TEXT NOT NULL PRIMARY KEY
        CHECK (length(trim(course_code)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    description TEXT CHECK (length(trim(description)) > 0),
    level TEXT NOT NULL CHECK (length(trim(level)) > 0),
    credits INT NOT NULL CHECK (credits > 0),
    department_id INT NOT NULL
        REFERENCES Department(department_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE Student (
    student_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    date_of_birth TEXT NOT NULL CHECK (
        date_of_birth GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(date_of_birth, '+0 days') IS date_of_birth
    ),
    email TEXT NOT NULL CHECK (length(trim(email)) > 0),
    phone TEXT CHECK (length(trim(phone)) > 0),
    programme_id INT NOT NULL
        REFERENCES Programme(programme_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    study_year INT NOT NULL CHECK (study_year > 0),
    graduation_status TEXT NOT NULL
        CHECK (graduation_status IN ('not_graduated', 'graduated')),
    advisor_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE LecturerQualification (
    lecturer_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    qualification_title TEXT NOT NULL
        CHECK (length(trim(qualification_title)) > 0),
    PRIMARY KEY (lecturer_id, qualification_title)
) STRICT;

CREATE TABLE DisciplinaryRecord (
    record_id INT NOT NULL PRIMARY KEY,
    student_id INT NOT NULL
        REFERENCES Student(student_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    incident_date TEXT NOT NULL CHECK (
        incident_date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(incident_date, '+0 days') IS incident_date
    ),
    description TEXT NOT NULL CHECK (length(trim(description)) > 0)
) STRICT;

CREATE TABLE CourseDelivery (
    delivery_id INT NOT NULL PRIMARY KEY,
    course_code TEXT NOT NULL
        REFERENCES Course(course_code)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    academic_year TEXT NOT NULL CHECK (length(trim(academic_year)) > 0),
    semester TEXT NOT NULL CHECK (length(trim(semester)) > 0),
    UNIQUE (course_code, academic_year, semester)
) STRICT;

CREATE TABLE ProgrammeCourse (
    programme_id INT NOT NULL
        REFERENCES Programme(programme_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    course_code TEXT NOT NULL
        REFERENCES Course(course_code)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (programme_id, course_code)
) STRICT;

CREATE TABLE CoursePrerequisite (
    course_code TEXT NOT NULL
        REFERENCES Course(course_code)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    prerequisite_code TEXT NOT NULL
        REFERENCES Course(course_code)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (course_code, prerequisite_code),
    CHECK (course_code <> prerequisite_code)
) STRICT;

CREATE TABLE Enrolment (
    student_id INT NOT NULL
        REFERENCES Student(student_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    delivery_id INT NOT NULL
        REFERENCES CourseDelivery(delivery_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    final_grade REAL CHECK (final_grade BETWEEN 0 AND 100),
    PRIMARY KEY (student_id, delivery_id)
) STRICT;

CREATE TABLE TeachingAssignment (
    lecturer_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    delivery_id INT NOT NULL
        REFERENCES CourseDelivery(delivery_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (lecturer_id, delivery_id)
) STRICT;

CREATE TABLE ResearchGroup (
    group_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    head_lecturer_id INT NOT NULL UNIQUE
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE ResearchProject (
    project_id INT NOT NULL PRIMARY KEY,
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    principal_investigator_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT
) STRICT;

CREATE TABLE ProjectLecturer (
    project_id INT NOT NULL
        REFERENCES ResearchProject(project_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    lecturer_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (project_id, lecturer_id)
) STRICT;

CREATE TABLE ProjectStudent (
    project_id INT NOT NULL
        REFERENCES ResearchProject(project_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    student_id INT NOT NULL
        REFERENCES Student(student_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (project_id, student_id)
) STRICT;

CREATE TABLE Organisation (
    organisation_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0)
) STRICT;

CREATE TABLE StudentOrganisation (
    student_id INT NOT NULL
        REFERENCES Student(student_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    organisation_id INT NOT NULL
        REFERENCES Organisation(organisation_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (student_id, organisation_id)
) STRICT;

CREATE TABLE Committee (
    committee_id INT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0)
) STRICT;

CREATE TABLE LecturerCommittee (
    lecturer_id INT NOT NULL
        REFERENCES Lecturer(lecturer_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    committee_id INT NOT NULL
        REFERENCES Committee(committee_id)
        ON UPDATE RESTRICT ON DELETE RESTRICT,
    PRIMARY KEY (lecturer_id, committee_id)
) STRICT;

COMMIT;
