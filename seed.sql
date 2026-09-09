PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

INSERT INTO Department (department_id, name, faculty) VALUES
    (1, 'Computing', 'Science'),
    (2, 'Business', 'Business and Management');

INSERT INTO Programme
    (programme_id, name, degree_awarded, duration_years)
VALUES
    (1, 'Computer Science', 'BSc', 3),
    (2, 'Business Management', 'BA', 4);

INSERT INTO Lecturer
    (lecturer_id, name, email, phone, department_id)
VALUES
    (1, 'Maya Patel', 'maya.patel@example.test', '02079460001', 1),
    (2, 'Owen Reed', 'owen.reed@example.test', NULL, 1),
    (3, 'Sofia Grant', 'sofia.grant@example.test', '02079460003', 2);

INSERT INTO NonAcademicStaff
    (staff_id, name, job_title, employment_type, salary, department_id)
VALUES
    (1, 'Noah Wilson', 'Laboratory Technician', 'Permanent', 35000.00, 1),
    (2, 'Priya Shah', 'Office Administrator', 'Part-time', 24000.00, 1),
    (3, 'Liam Brooks', 'Programme Coordinator', 'Fixed-term', NULL, 2);

INSERT INTO Course
    (course_code, name, description, level, credits, department_id)
VALUES
    ('CS101', 'Programming Fundamentals',
     'Introduction to programming.', 'Level 4', 15, 1),
    ('CS201', 'Database Systems',
     'Relational modelling and SQL.', 'Level 5', 15, 1),
    ('CS301', 'Data Analytics',
     'Analysis and interpretation of data.', 'Level 6', 30, 1),
    ('BU101', 'Principles of Management',
     'Introduction to management.', 'Level 4', 15, 2),
    ('BU201', 'Business Research Methods',
     'Research methods for business.', 'Level 5', 15, 2),
    ('BU401', 'Business Strategy',
     NULL, 'Level 6', 30, 2);

INSERT INTO Student
    (student_id, name, date_of_birth, email, phone,
     programme_id, study_year, graduation_status, advisor_id)
VALUES
    (1, 'Amina Yusuf', '2004-03-12', 'amina.yusuf@example.test',
     '02079460101', 1, 3, 'not_graduated', 1),
    (2, 'Ben Carter', '2004-08-25', 'ben.carter@example.test',
     NULL, 1, 3, 'not_graduated', 1),
    (3, 'Chloe Martin', '2004-02-29', 'chloe.martin@example.test',
     '02079460103', 1, 3, 'not_graduated', 2),
    (4, 'Daniel Okafor', '2003-11-09', 'daniel.okafor@example.test',
     NULL, 1, 3, 'not_graduated', 2),
    (5, 'Ella Chen', '2005-06-17', 'ella.chen@example.test',
     '02079460105', 1, 2, 'not_graduated', 1),
    (6, 'Farah Ali', '2003-01-22', 'farah.ali@example.test',
     NULL, 1, 3, 'not_graduated', 2),
    (7, 'George Evans', '2003-09-04', 'george.evans@example.test',
     '02079460107', 2, 4, 'not_graduated', 3),
    (8, 'Hannah Reed', '2001-05-15', 'hannah.reed@example.test',
     NULL, 2, 4, 'graduated', 3),
    (9, 'Isaac Patel', '2004-12-02', 'isaac.patel@example.test',
     NULL, 1, 3, 'not_graduated', 1),
    (10, 'Jack Morgan', '2008-04-19', 'jack.morgan@example.test',
     NULL, 1, 1, 'not_graduated', 2);

INSERT INTO LecturerQualification
    (lecturer_id, qualification_title)
VALUES
    (1, 'PhD in Computer Science'),
    (1, 'MSc in Data Science'),
    (2, 'PhD in Information Systems'),
    (2, 'MSc in Computing'),
    (3, 'PhD in Management'),
    (3, 'MBA');

INSERT INTO DisciplinaryRecord
    (record_id, student_id, incident_date, description)
VALUES
    (1, 2, '2025-11-03', 'Late return of university equipment.'),
    (2, 2, '2026-02-12', 'Breach of library conduct policy.');

INSERT INTO CourseDelivery
    (delivery_id, course_code, academic_year, semester)
VALUES
    (1, 'CS101', '2024/25', '1'),
    (2, 'CS201', '2024/25', '2'),
    (3, 'BU101', '2025/26', '1'),
    (4, 'BU201', '2025/26', '2'),
    (5, 'CS301', '2026/27', '1'),
    (6, 'CS201', '2026/27', '1'),
    (7, 'BU401', '2026/27', '1'),
    (8, 'CS301', '2025/26', '1'),
    (9, 'CS201', '2026/27', '2');

INSERT INTO ProgrammeCourse (programme_id, course_code) VALUES
    (1, 'CS101'),
    (1, 'CS201'),
    (1, 'CS301'),
    (2, 'BU101'),
    (2, 'BU201'),
    (2, 'BU401'),
    (2, 'CS301');

INSERT INTO CoursePrerequisite
    (course_code, prerequisite_code)
VALUES
    ('CS201', 'CS101'),
    ('CS301', 'CS201'),
    ('BU201', 'BU101'),
    ('BU401', 'BU201');

INSERT INTO Enrolment
    (student_id, delivery_id, final_grade)
VALUES
    (1, 2, 70),
    (1, 1, 80),
    (1, 5, NULL),
    (2, 2, 65),
    (2, 1, 75),
    (2, 5, NULL),
    (3, 2, 60),
    (3, 1, 68),
    (3, 5, NULL),
    (4, 5, NULL),
    (5, 1, 90),
    (5, 6, NULL),
    (6, 8, 0),
    (7, 3, 60),
    (7, 4, 100),
    (7, 7, NULL),
    (8, 3, 60),
    (8, 4, 70),
    (9, 9, NULL);

INSERT INTO TeachingAssignment (lecturer_id, delivery_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (3, 4),
    (1, 5),
    (2, 5),
    (2, 6),
    (3, 7),
    (2, 8),
    (2, 9);

INSERT INTO ResearchGroup (group_id, name, head_lecturer_id) VALUES
    (1, 'Data Research Group', 1),
    (2, 'Business Research Group', 3);

INSERT INTO ResearchProject
    (project_id, title, principal_investigator_id)
VALUES
    (1, 'University Energy Data Analysis', 1),
    (2, 'Student Enterprise Study', 3);

INSERT INTO ProjectLecturer (project_id, lecturer_id) VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (2, 2);

INSERT INTO ProjectStudent (project_id, student_id) VALUES
    (1, 1),
    (1, 3),
    (2, 7),
    (2, 1);

INSERT INTO Organisation (organisation_id, name) VALUES
    (1, 'Computing Society'),
    (2, 'Student Volunteers');

INSERT INTO StudentOrganisation (student_id, organisation_id) VALUES
    (1, 1),
    (2, 1),
    (1, 2),
    (7, 2);

INSERT INTO Committee (committee_id, name) VALUES
    (1, 'Teaching Committee'),
    (2, 'Research Committee');

INSERT INTO LecturerCommittee (lecturer_id, committee_id) VALUES
    (1, 1),
    (2, 1),
    (1, 2),
    (3, 2);

COMMIT;
