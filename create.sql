-- Active: 1681930813804@@phase-2-group2.cnleqhafy7wq.us-east-1.rds.amazonaws.com@3306@university

use university;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uid         int(8) AUTO_INCREMENT NOT NULL UNIQUE, 
    fname       varchar(50) NOT NULL,
    minit       char(1) DEFAULT NULL,
    lname       varchar(50) NOT NULL,
    email       varchar(50) NOT NULL UNIQUE,
    password    varchar(50) NOT NULL,
    address     varchar(100) NOT NULL,
    ssn         char(9) NOT NULL UNIQUE,
    user_type   enum('Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar') NOT NULL,
    PRIMARY KEY (uid)
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
    uid         int(8) NOT NULL UNIQUE,
    dept        varchar(50) DEFAULT NULL,
    is_CAC      enum('T', 'F') DEFAULT 'F' NOT NULL,
    can_teach   enum('T', 'F') DEFAULT 'F' NOT NULL,
    can_advise  enum('T', 'F') DEFAULT 'F' NOT NULL,
    can_review  enum('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY (uid), 
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students (
    uid         int(8) NOT NULL UNIQUE,
    degree      enum('Masters', 'PHD') NOT NULL,
    advisor_id  int(8) NOT NULL,
    suspended   enum('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY (uid), 
    FOREIGN KEY (uid) REFERENCES users(uid),
    FOREIGN KEY (advisor_id) REFERENCES users(uid)
);

DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
    cid             int(8) AUTO_INCREMENT NOT NULL UNIQUE,
    department      varchar(8) NOT NULL,
    class_num       int(8) NOT NULL,
    class_title     varchar(32) NOT NULL,
    credit_hours    int(1) NOT NULL,
    PRIMARY KEY (cid), 
    CONSTRAINT uc_classes UNIQUE (department, class_num)
);

DROP TABLE IF EXISTS valid_semesters;
CREATE TABLE valid_semesters (
    year            int(4) NOT NULL,
    semester        ENUM('1', '2', '3') NOT NULL,
    can_register    ENUM('T', 'F') DEFAULT 'F' NOT NULL,
    current_sem     ENUM('T', 'F') DEFAULT 'F' NOT NULL,
    is_done         ENUM('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY(year, semester)
);

DROP TABLE IF EXISTS current_sections; 
CREATE TABLE current_sections (
    cid             int(8) NOT NULL,
    section_id      varchar(16) NOT NULL UNIQUE,
    professor_uid   int(8) NOT NULL,
    year            int(4) NOT NULL,
    semester        enum('1','2','3') NOT NULL,     
    day             enum('M', 'T', 'W', 'R', 'F') NOT NULL,
    timeslot        enum('1', '2', '3') NOT NULL,
    PRIMARY KEY (section_id),
    FOREIGN KEY (cid) REFERENCES classes(cid),
    FOREIGN KEY (professor_uid) REFERENCES users(uid),
    FOREIGN KEY (year, semester) REFERENCES valid_semesters(year, semester)
);

DROP TABLE IF EXISTS prerequisites; 
CREATE TABLE prerequisites (
    class_cid   int(8) NOT NULL,
    prereq_cid  int(8) NOT NULL,
    PRIMARY KEY (class_cid, prereq_cid), 
    FOREIGN KEY (class_cid) REFERENCES classes(cid),
    FOREIGN KEY (prereq_cid) REFERENCES classes(cid)
);


DROP TABLE IF EXISTS student_classes; 
CREATE TABLE student_classes (
    student_uid     int(8) NOT NULL,
    cid             int(8) NOT NULL,
    section_id      varchar(16) NOT NULL,
    grade           enum('IP', 'A', 'A-', 'B+' ,'B', 'B-', 'C+', 'C', 'F'),
    PRIMARY KEY (student_uid, section_id),
    FOREIGN KEY (student_uid) REFERENCES users(uid),
    FOREIGN KEY (cid) REFERENCES classes(cid),
    FOREIGN KEY (section_id) REFERENCES current_sections(section_id)
);

DROP TABLE IF EXISTS advisor_hold_classes;
CREATE TABLE advisor_hold_classes (
    student_uid     int(8) NOT NULL,
    cid             int(8) NOT NULL,
    section_id      varchar(16) NOT NULL,
    submitted       ENUM('T', 'F') DEFAULT 'F' NOT NULL,
    approved        ENUM('T', 'F') DEFAULT 'F' NOT NULL,
    year            int(4) NOT NULL,
    semester        ENUM('1', '2', '3'),
    PRIMARY KEY (student_uid, section_id),
    FOREIGN KEY (student_uid) REFERENCES users(uid),
    FOREIGN KEY (cid) REFERENCES classes(cid),
    FOREIGN KEY (section_id) REFERENCES current_sections(section_id)
);

DROP TABLE IF EXISTS form1; 
CREATE TABLE form1 (
    user_id     int(8) NOT NULL,
    cid         int(8) NOT NULL,
    PRIMARY KEY (user_id, cid),
    FOREIGN KEY (user_id) REFERENCES users(uid),
    FOREIGN KEY (cid)  REFERENCES  classes(cid)
);

DROP TABLE IF EXISTS grad_requests; 
CREATE TABLE grad_requests (
    student_id      int(8) NOT NULL UNIQUE,
    advisor_id      int(8) NOT NULL,
    approved        enum('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY (student_id),
    FOREIGN KEY (student_id) REFERENCES users(uid),
    FOREIGN KEY (advisor_id)  REFERENCES users(uid)
);

DROP TABLE IF EXISTS phd_thesis; 
CREATE TABLE phd_thesis (
    user_id     int(8) NOT NULL UNIQUE,
    thesis      varchar(50),
    approved    enum('T', 'F') DEFAULT 'F' NOT NULL,
    PRIMARY KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES users(uid)
);

DROP TABLE IF EXISTS applications;
CREATE TABLE applications (
    uid         int(8) NOT NULL UNIQUE,
    status      enum('incomplete', 'complete', 'admitted', 'denied' , 'admitaid', 'acceptdeposit', 'student') NOT NULL,
    transcript  enum('T', 'F', 'M') DEFAULT 'F' NOT NULL,
    degree      enum('MS', 'PhD') NOT NULL,
    semester    enum('Fall', 'Spring') NOT NULL,
    year        int(4) NOT NULL,
    experience  varchar(300) NOT NULL,
    aoi         varchar(300) NOT NULL,
    received    DATE NOT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS degrees;
CREATE TABLE degrees (
    uid         int(8) NOT NULL,
    type        enum('BS/BA', 'MS') NOT NULL,
    gpa         decimal(3,2) NOT NULL, 
    major       varchar(50) NOT NULL,
    college     varchar(50) NOT NULL,
    year        int(4) NOT NULL,
    PRIMARY KEY (uid, type),
    FOREIGN KEY (uid) REFERENCES users(uid),
    CONSTRAINT past_deg UNIQUE (uid, type)
);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    uid         int(8) NOT NULL,
    rating      ENUM('0','1','2','3') NOT NULL,
    deficiency  varchar(100) DEFAULT NULL,
    reason      char(1) DEFAULT NULL,
    advisor_id  int(8) NOT NULL,
    comments    varchar(40) NOT NULL,
    reviewer_id int(8) NOT NULL,
    PRIMARY KEY (uid, reviewer_id),
    FOREIGN KEY (uid) REFERENCES users(uid),
    FOREIGN KEY (advisor_id) REFERENCES users(uid),
    FOREIGN KEY (reviewer_id) REFERENCES users(uid),
    CONSTRAINT us_rev UNIQUE (uid, reviewer_id)
);

DROP TABLE IF EXISTS gres;
CREATE TABLE gres (
    uid         int(8) NOT NULL UNIQUE,
    total       int(3) DEFAULT NULL,
    verbal      int(3) DEFAULT NULL,
    quant       int(3) DEFAULT NULL,
    year        int(4) DEFAULT NULL,
    toefl       int(3) DEFAULT NULL,
    score       int(3) DEFAULT NULL,
    subject     varchar(30) DEFAULT NULL,
    date        int(4) DEFAULT NULL,
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS recs;
CREATE TABLE recs (
    uid         int(8) NOT NULL,
    sent        varchar(50) DEFAULT NULL,
    rating      enum('1','2','3','4','5'),
    generic     enum('Y','N'),
    credible    enum('Y','N'),
    writer      varchar(30) NOT NULL,
    email       varchar(50) NOT NULL,
    title       varchar(30) NOT NULL,
    affiliation varchar(30) NOT NULL,
    message     varchar(200) DEFAULT NULL,
    PRIMARY KEY (uid, email),
    FOREIGN KEY(uid) REFERENCES users(uid),
    CONSTRAINT rec_email UNIQUE (uid, email)
);

SET FOREIGN_KEY_CHECKS = 1;

-- add classes
INSERT INTO classes VALUES (1,'CSCI',6221,'SW Paradigms',3);
INSERT INTO classes VALUES (2,'CSCI',6461,'Computer Architecture',3);
INSERT INTO classes VALUES (3,'CSCI',6212,'Algorithms',3);
INSERT INTO classes VALUES (4,'CSCI',6220,'Machine Learning',3);
INSERT INTO classes VALUES (5,'CSCI',6232,'Networks 1',3);
INSERT INTO classes VALUES (6,'CSCI',6233,'Networks 2',3);
INSERT INTO classes VALUES (7,'CSCI',6241,'Database 1',3);
INSERT INTO classes VALUES (8,'CSCI',6242,'Database 2',3);
INSERT INTO classes VALUES (9,'CSCI',6246,'Compilers',3);
INSERT INTO classes VALUES (10,'CSCI',6260,'Multimedia',3);
INSERT INTO classes VALUES (11,'CSCI',6251,'Cloud Computing',3);
INSERT INTO classes VALUES (12,'CSCI',6254,'SW Engineering',3);
INSERT INTO classes VALUES (13,'CSCI',6262,'Graphics 1',3);
INSERT INTO classes VALUES (14,'CSCI',6283,'Security 1',3);
INSERT INTO classes VALUES (15,'CSCI',6284,'Cryptography',3);
INSERT INTO classes VALUES (16,'CSCI',6286,'Network Security',3);
INSERT INTO classes VALUES (17,'CSCI',6325,'Algorithms 2',3);
INSERT INTO classes VALUES (18,'CSCI',6339,'Embedded Systems',3);
INSERT INTO classes VALUES (19,'CSCI',6384,'Cryptography 2',3);
INSERT INTO classes VALUES (20,'ECE',6241,'Communication Theory',3);
INSERT INTO classes VALUES (21,'ECE',6242,'Information Theory',2);
INSERT INTO classes VALUES (22,'MATH',6210,'Logic',2);

-- add valid semesters
INSERT INTO valid_semesters VALUES (2023, 1, "F", "F", "T");
INSERT INTO valid_semesters VALUES (2023, 2, "F", "F", "T");
INSERT INTO valid_semesters VALUES (2023, 3, "T", "T", "F");
INSERT INTO valid_semesters VALUES (2024, 1, "T", "F", "T");
INSERT INTO valid_semesters VALUES (2024, 2, "F", "F", "F");
INSERT INTO valid_semesters VALUES (2024, 3, "F", "F", "F");

-- add prereqs
INSERT INTO prerequisites VALUES (6,5);
INSERT INTO prerequisites VALUES (8,7);
INSERT INTO prerequisites VALUES (9,2);
INSERT INTO prerequisites VALUES (9,3);
INSERT INTO prerequisites VALUES (11,2);
INSERT INTO prerequisites VALUES (12,1);
INSERT INTO prerequisites VALUES (14,3);
INSERT INTO prerequisites VALUES (15,3);
INSERT INTO prerequisites VALUES (16,14);
INSERT INTO prerequisites VALUES (16,5);
INSERT INTO prerequisites VALUES (17,3);
INSERT INTO prerequisites VALUES (18,2);
INSERT INTO prerequisites VALUES (18,3);
INSERT INTO prerequisites VALUES (19,15);

-- add users 
INSERT INTO users VALUES (90000001, "Sys", "a", "Admin", "admin@school.edu", "pass", "123 4th st", "111111111", "Admin");
INSERT INTO users VALUES (90000002, "Grad", "s", "Sec", "GS@school.edu", "pass", "123 4th st", "111111112", "GS");
INSERT INTO users VALUES (90000007, "Reg", "r", "Registrar", "registrar@school.edu", "pass", "123 4th st", "111111117", "Registrar");
INSERT INTO users VALUES (90000008, "Department", "c", "Chair", "cac@school.edu", "pass", "123 4th st", "111111118", "Faculty");
INSERT INTO users VALUES (90000009, "Fac", "r", "Reviewer", "reviewer@school.edu", "pass", "123 4th st", "111111119", "Faculty");
INSERT INTO users VALUES (90000010, "Fac", "a", "Advisor", "advisor@school.edu", "pass", "123 4th st", "111111120", "Faculty");
INSERT INTO users VALUES (90000011, "Hyeong-Ah", "c", "Choi", "choi@school.edu", "pass", "123 4th st", "111111121", "Faculty");
INSERT INTO users VALUES (90000012, "Rachelle", "s", "Heller", "heller@school.edu", "pass", "123 4th st", "111111122", "Faculty");
INSERT INTO users VALUES (90000013, "Bhagirath", "f", "Narahari", "narahari@school.edu", "pass", "123 4th st", "111111123", "Faculty");
INSERT INTO users VALUES (90000014, "Gabe", "a", "Parmer", "parmer@school.edu", "pass", "123 4th st", "111111124", "Faculty");
INSERT INTO users VALUES (90000015, "Tim", "w", "Wood", "wood@school.edu", "pass", "123 4th st", "111111125", "Faculty");
INSERT INTO users VALUES (90000016, "James", "t", "Taylor", "taylor@school.edu", "pass", "123 4th st", "111111126", "Faculty");


-- add faculty
INSERT INTO faculty VALUES(90000008, "CSCI", "T", "T", "T", "T");
INSERT INTO faculty VALUES(90000009, "CSCI", "F", "F", "F", "T");
INSERT INTO faculty VALUES(90000010, "CSCI", "F", "F", "T", "F");
INSERT INTO faculty VALUES(90000011, "CSCI", "F", "T", "T", "T");
INSERT INTO faculty VALUES(90000012, "CSCI", "F", "F", "T", "T");
INSERT INTO faculty VALUES(90000013, "CSCI", "F", "T", "T", "T");
INSERT INTO faculty VALUES(90000014, "CSCI", "F", "T", "T", "F");
INSERT INTO faculty VALUES(90000015, "CSCI", "F", "T", "T", "T");
INSERT INTO faculty VALUES(90000016, "CSCI", "F", "F", "F", "F");

-- add sections
INSERT INTO current_sections VALUES (1,'2023-1-1-1','90000008',2023,1,'M',1);
INSERT INTO current_sections VALUES (2,'2023-1-2-1','90000013',2023,1,'T',1);
INSERT INTO current_sections VALUES (3,'2023-1-3-1','90000011',2023,1,'W',1);
INSERT INTO current_sections VALUES (5,'2023-1-5-1','90000008',2023,1,'M',3);
INSERT INTO current_sections VALUES (6,'2023-1-6-1','90000008',2023,1,'T',3);
INSERT INTO current_sections VALUES (7,'2023-1-7-1','90000008',2023,1,'W',3);
INSERT INTO current_sections VALUES (8,'2023-1-8-1','90000008',2023,1,'R',3);
INSERT INTO current_sections VALUES (9,'2023-1-9-1','90000014',2023,1,'T',1);
INSERT INTO current_sections VALUES (11,'2023-1-11-1','90000014',2023,1,'M',3);
INSERT INTO current_sections VALUES (12,'2023-1-12-1','90000014',2023,1,'M',1);
INSERT INTO current_sections VALUES (10,'2023-1-10-1','90000014',2023,1,'R',3);
INSERT INTO current_sections VALUES (13,'2023-1-13-1','90000014',2023,1,'W',3);
INSERT INTO current_sections VALUES (14,'2023-1-14-1','90000014',2023,1,'T',3);
INSERT INTO current_sections VALUES (15,'2023-1-15-1','90000015',2023,1,'M',3);
INSERT INTO current_sections VALUES (16,'2023-1-16-1','90000015',2023,1,'W',3);
INSERT INTO current_sections VALUES (19,'2023-1-19-1','90000015',2023,1,'W',1);
INSERT INTO current_sections VALUES (20,'2023-1-20-1','90000011',2023,1,'M',3);
INSERT INTO current_sections VALUES (21,'2023-1-21-1','90000011',2023,1,'T',3);
INSERT INTO current_sections VALUES (22,'2023-1-22-1','90000011',2023,1,'W',3);
INSERT INTO current_sections VALUES (18,'2023-1-18-1','90000011',2023,1,'R',2);

-- 2023 2
INSERT INTO current_sections VALUES (1,'2023-2-1-1','90000008',2023,2,'M',1);
INSERT INTO current_sections VALUES (2,'2023-2-2-1','90000013',2023,2,'T',1);
INSERT INTO current_sections VALUES (3,'2023-2-3-1','90000011',2023,2,'W',1);
INSERT INTO current_sections VALUES (5,'2023-2-5-1','90000008',2023,2,'M',3);
INSERT INTO current_sections VALUES (6,'2023-2-6-1','90000008',2023,2,'T',3);
INSERT INTO current_sections VALUES (7,'2023-2-7-1','90000008',2023,2,'W',3);
INSERT INTO current_sections VALUES (8,'2023-2-8-1','90000008',2023,2,'R',3);
INSERT INTO current_sections VALUES (9,'2023-2-9-1','90000014',2023,2,'T',1);
INSERT INTO current_sections VALUES (11,'2023-2-11-1','90000014',2023,2,'M',3);
INSERT INTO current_sections VALUES (12,'2023-2-12-1','90000014',2023,2,'M',1);
INSERT INTO current_sections VALUES (10,'2023-2-10-1','90000014',2023,2,'R',3);
INSERT INTO current_sections VALUES (13,'2023-2-13-1','90000014',2023,2,'W',3);
INSERT INTO current_sections VALUES (14,'2023-2-14-1','90000014',2023,2,'T',3);
INSERT INTO current_sections VALUES (15,'2023-2-15-1','90000015',2023,2,'M',3);
INSERT INTO current_sections VALUES (16,'2023-2-16-1','90000015',2023,2,'W',3);
INSERT INTO current_sections VALUES (19,'2023-2-19-1','90000015',2023,2,'W',1);
INSERT INTO current_sections VALUES (20,'2023-2-20-1','90000011',2023,2,'M',3);
INSERT INTO current_sections VALUES (21,'2023-2-21-1','90000011',2023,2,'T',3);
INSERT INTO current_sections VALUES (22,'2023-2-22-1','90000011',2023,2,'W',3);
INSERT INTO current_sections VALUES (18,'2023-2-18-1','90000011',2023,2,'R',2);

-- 2023 3
INSERT INTO current_sections VALUES (1,'2023-3-1-1','90000008',2023,3,'M',1);
INSERT INTO current_sections VALUES (2,'2023-3-2-1','90000013',2023,3,'T',1);
INSERT INTO current_sections VALUES (3,'2023-3-3-1','90000011',2023,3,'W',1);
INSERT INTO current_sections VALUES (5,'2023-3-5-1','90000008',2023,3,'M',3);
INSERT INTO current_sections VALUES (6,'2023-3-6-1','90000008',2023,3,'T',3);
INSERT INTO current_sections VALUES (7,'2023-3-7-1','90000008',2023,3,'W',3);
INSERT INTO current_sections VALUES (8,'2023-3-8-1','90000008',2023,3,'R',3);
INSERT INTO current_sections VALUES (9,'2023-3-9-1','90000014',2023,3,'T',1);
INSERT INTO current_sections VALUES (11,'2023-3-11-1','90000014',2023,3,'M',3);
INSERT INTO current_sections VALUES (12,'2023-3-12-1','90000014',2023,3,'M',1);
INSERT INTO current_sections VALUES (10,'2023-3-10-1','90000014',2023,3,'R',3);
INSERT INTO current_sections VALUES (13,'2023-3-13-1','90000014',2023,3,'W',3);
INSERT INTO current_sections VALUES (14,'2023-3-14-1','90000014',2023,3,'T',3);
INSERT INTO current_sections VALUES (15,'2023-3-15-1','90000015',2023,3,'M',3);
INSERT INTO current_sections VALUES (16,'2023-3-16-1','90000015',2023,3,'W',3);
INSERT INTO current_sections VALUES (19,'2023-3-19-1','90000015',2023,3,'W',1);
INSERT INTO current_sections VALUES (20,'2023-3-20-1','90000011',2023,3,'M',3);
INSERT INTO current_sections VALUES (21,'2023-3-21-1','90000011',2023,3,'T',3);
INSERT INTO current_sections VALUES (22,'2023-3-22-1','90000011',2023,3,'W',3);
INSERT INTO current_sections VALUES (18,'2023-3-18-1','90000011',2023,3,'R',2);

-- 2024 1
INSERT INTO current_sections VALUES (1,'2024-1-1-1','90000008',2024,1,'M',1);
INSERT INTO current_sections VALUES (2,'2024-1-2-1','90000013',2024,1,'T',1);
INSERT INTO current_sections VALUES (3,'2024-1-3-1','90000011',2024,1,'W',1);
INSERT INTO current_sections VALUES (5,'2024-1-5-1','90000008',2024,1,'M',3);
INSERT INTO current_sections VALUES (6,'2024-1-6-1','90000008',2024,1,'T',3);
INSERT INTO current_sections VALUES (7,'2024-1-7-1','90000008',2024,1,'W',3);
INSERT INTO current_sections VALUES (8,'2024-1-8-1','90000008',2024,1,'R',3);
INSERT INTO current_sections VALUES (9,'2024-1-9-1','90000014',2024,1,'T',1);
INSERT INTO current_sections VALUES (11,'2024-1-11-1','90000014',2024,1,'M',3);
INSERT INTO current_sections VALUES (12,'2024-1-12-1','90000014',2024,1,'M',1);
INSERT INTO current_sections VALUES (10,'2024-1-10-1','90000014',2024,1,'R',3);
INSERT INTO current_sections VALUES (13,'2024-1-13-1','90000014',2024,1,'W',3);
INSERT INTO current_sections VALUES (14,'2024-1-14-1','90000014',2024,1,'T',3);
INSERT INTO current_sections VALUES (15,'2024-1-15-1','90000015',2024,1,'M',3);
INSERT INTO current_sections VALUES (16,'2024-1-16-1','90000015',2024,1,'W',3);
INSERT INTO current_sections VALUES (19,'2024-1-19-1','90000015',2024,1,'W',1);
INSERT INTO current_sections VALUES (20,'2024-1-20-1','90000011',2024,1,'M',3);
INSERT INTO current_sections VALUES (21,'2024-1-21-1','90000011',2024,1,'T',3);
INSERT INTO current_sections VALUES (22,'2024-1-22-1','90000011',2024,1,'W',3);
INSERT INTO current_sections VALUES (18,'2024-1-18-1','90000011',2024,1,'R',2);

-- 2024 2
INSERT INTO current_sections VALUES (1,'2024-2-1-1','90000008',2024,2,'M',1);
INSERT INTO current_sections VALUES (2,'2024-2-2-1','90000013',2024,2,'T',1);
INSERT INTO current_sections VALUES (3,'2024-2-3-1','90000011',2024,2,'W',1);
INSERT INTO current_sections VALUES (5,'2024-2-5-1','90000008',2024,2,'M',3);
INSERT INTO current_sections VALUES (6,'2024-2-6-1','90000008',2024,2,'T',3);
INSERT INTO current_sections VALUES (7,'2024-2-7-1','90000008',2024,2,'W',3);
INSERT INTO current_sections VALUES (8,'2024-2-8-1','90000008',2024,2,'R',3);
INSERT INTO current_sections VALUES (9,'2024-2-9-1','90000014',2024,2,'T',1);
INSERT INTO current_sections VALUES (11,'2024-2-11-1','90000014',2024,2,'M',3);
INSERT INTO current_sections VALUES (12,'2024-2-12-1','90000014',2024,2,'M',1);
INSERT INTO current_sections VALUES (10,'2024-2-10-1','90000014',2024,2,'R',3);
INSERT INTO current_sections VALUES (13,'2024-2-13-1','90000014',2024,2,'W',3);
INSERT INTO current_sections VALUES (14,'2024-2-14-1','90000014',2024,2,'T',3);
INSERT INTO current_sections VALUES (15,'2024-2-15-1','90000015',2024,2,'M',3);
INSERT INTO current_sections VALUES (16,'2024-2-16-1','90000015',2024,2,'W',3);
INSERT INTO current_sections VALUES (19,'2024-2-19-1','90000015',2024,2,'W',1);
INSERT INTO current_sections VALUES (20,'2024-2-20-1','90000011',2024,2,'M',3);
INSERT INTO current_sections VALUES (21,'2024-2-21-1','90000011',2024,2,'T',3);
INSERT INTO current_sections VALUES (22,'2024-2-22-1','90000011',2024,2,'W',3);
INSERT INTO current_sections VALUES (18,'2024-2-18-1','90000011',2024,2,'R',2);

-- 2024 3
INSERT INTO current_sections VALUES (1,'2024-3-1-1','90000008',2024,3,'M',1);
INSERT INTO current_sections VALUES (2,'2024-3-2-1','90000013',2024,3,'T',1);
INSERT INTO current_sections VALUES (3,'2024-3-3-1','90000011',2024,3,'W',1);
INSERT INTO current_sections VALUES (5,'2024-3-5-1','90000008',2024,3,'M',3);
INSERT INTO current_sections VALUES (6,'2024-3-6-1','90000008',2024,3,'T',3);
INSERT INTO current_sections VALUES (7,'2024-3-7-1','90000008',2024,3,'W',3);
INSERT INTO current_sections VALUES (8,'2024-3-8-1','90000008',2024,3,'R',3);
INSERT INTO current_sections VALUES (9,'2024-3-9-1','90000014',2024,3,'T',1);
INSERT INTO current_sections VALUES (11,'2024-3-11-1','90000014',2024,3,'M',3);
INSERT INTO current_sections VALUES (12,'2024-3-12-1','90000014',2024,3,'M',1);
INSERT INTO current_sections VALUES (10,'2024-3-10-1','90000014',2024,3,'R',3);
INSERT INTO current_sections VALUES (13,'2024-3-13-1','90000014',2024,3,'W',3);
INSERT INTO current_sections VALUES (14,'2024-3-14-1','90000014',2024,3,'T',3);
INSERT INTO current_sections VALUES (15,'2024-3-15-1','90000015',2024,3,'M',3);
INSERT INTO current_sections VALUES (16,'2024-3-16-1','90000015',2024,3,'W',3);
INSERT INTO current_sections VALUES (19,'2024-3-19-1','90000015',2024,3,'W',1);
INSERT INTO current_sections VALUES (20,'2024-3-20-1','90000011',2024,3,'M',3);
INSERT INTO current_sections VALUES (21,'2024-3-21-1','90000011',2024,3,'T',3);
INSERT INTO current_sections VALUES (22,'2024-3-22-1','90000011',2024,3,'W',3);
INSERT INTO current_sections VALUES (18,'2024-3-18-1','90000011',2024,3,'R',2);

-- add users 
INSERT INTO users VALUES(88888888, "Billie", "", "Holiday", "holiday@school.edu", "pass", "123 4th st", "888888888", "Student");
INSERT INTO students VALUES(88888888, "Masters", 90000008, 'F');
INSERT INTO applications VALUES(88888888, "student", "T", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");

INSERT INTO users VALUES(99999990, "Diana", "", "Krall", "krall@school.edu", "pass", "123 4th st", "999999999", "Student");
INSERT INTO students VALUES(99999990, "Masters", 90000008, "F");
INSERT INTO applications VALUES(99999990, "student", "T", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");

INSERT INTO users VALUES(12312312, "John", "", "Lennon", "lennon@email.com", "pass", "123 4th st", "111-111-111", "Applicant");
INSERT INTO applications VALUES(12312312, "complete", "T", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO degrees VALUES(12312312, "BS/BA", 4.00, "CSCI", "GWU", 2020);
INSERT INTO recs VALUES(12312312, "send me a rec pls", Null, Null, Null, "First Recommender", "rec1@email.com", "Prof", "Prof", "you're a great student");

INSERT INTO users VALUES(66666666, "Ringo", "", "Starr", "starr@email.com", "pass", "123 4th st", "222-11-1111", "Applicant");
INSERT INTO applications VALUES(66666666, "incomplete", "F", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO degrees VALUES(66666666, "BS/BA", 3.56, "CSCI", "GWU", 2020);
INSERT INTO recs VALUES(66666666, Null, Null, Null, Null, "Another Recommender", "rec2@email.com", "Prof", "Prof", Null);

INSERT INTO users VALUES(55555555,  "Paul", "", "McCartney", "mccartney@school.edu", "pass", "123 4th st", "555555555", "Student");
INSERT INTO students VALUES(55555555, "Masters", 90000013, "F");
INSERT INTO applications VALUES(55555555, "student", "F", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO student_classes VALUES(55555555, '1', '2023-1-1-1', 'A');
INSERT INTO student_classes VALUES(55555555, '3', '2023-1-3-1', 'A');
INSERT INTO student_classes VALUES(55555555, '2', '2023-1-2-1', 'A');
INSERT INTO student_classes VALUES(55555555, '5', '2023-1-5-1', 'A');
INSERT INTO student_classes VALUES(55555555, '7', '2023-1-7-1', 'A');
INSERT INTO student_classes VALUES(55555555, '9', '2023-1-9-1', 'B');
INSERT INTO student_classes VALUES(55555555, '13', '2023-1-13-1', 'B');
INSERT INTO student_classes VALUES(55555555, '14', '2023-1-14-1', 'B');
INSERT INTO student_classes VALUES(55555555, '8', '2023-1-8-1', 'B');
INSERT INTO student_classes VALUES(55555555, '6', '2023-1-6-1', 'B');


INSERT INTO users VALUES(66666667,  "George", "", "Harrison", "harrison@school.edu", "pass", "123 4th st", "666666667", "Student");
INSERT INTO students VALUES(66666667, "Masters", 90000014, "F");
INSERT INTO applications VALUES(66666667, "student", "F", "MS", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO student_classes VALUES (66666667, '1', '2023-1-1-1', 'C');
INSERT INTO student_classes VALUES (66666667, '2', '2023-1-2-1', 'B');
INSERT INTO student_classes VALUES (66666667, '3', '2023-1-3-1', 'B');
INSERT INTO student_classes VALUES (66666667, '5', '2023-1-5-1', 'B');
INSERT INTO student_classes VALUES (66666667, '6', '2023-1-6-1', 'B');
INSERT INTO student_classes VALUES (66666667, '7', '2023-1-7-1', 'B');
INSERT INTO student_classes VALUES (66666667, '8', '2023-1-8-1', 'B');
INSERT INTO student_classes VALUES (66666667, '14', '2023-1-14-1', 'B');
INSERT INTO student_classes VALUES (66666667, '15', '2023-1-15-1', 'B');


INSERT INTO users VALUES (12121212, "Ringo2", "2", "Starr2", "starr2@school.edu",   "pass", "123 4th st", "121212121", "Student");
INSERT INTO students VALUES(12121212, "PHD", 90000014, "F");
INSERT INTO applications VALUES(12121212, "student", "F", "PhD", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO student_classes VALUES (12121212,'1','2024-3-1-1','A');
INSERT INTO student_classes VALUES (12121212,'2','2023-3-2-1','A');
INSERT INTO student_classes VALUES (12121212,'3','2023-3-3-1','A');
INSERT INTO student_classes VALUES (12121212,'5','2023-1-5-1','A');
INSERT INTO student_classes VALUES (12121212,'6','2023-3-6-1','A');
INSERT INTO student_classes VALUES (12121212,'7','2024-3-7-1','A');
INSERT INTO student_classes VALUES (12121212,'8','2024-3-8-1','A');
INSERT INTO student_classes VALUES (12121212,'9','2024-2-9-1','A');
INSERT INTO student_classes VALUES (12121212,'10','2024-2-10-1','A');
INSERT INTO student_classes VALUES (12121212,'11','2024-3-11-1','A');
INSERT INTO student_classes VALUES (12121212,'12','2024-2-12-1','A');
INSERT INTO student_classes VALUES (12121212,'13','2023-3-13-1','A');
INSERT INTO phd_thesis VALUES(12121212, "this is my thesis", "F");

INSERT INTO users VALUES(77777777, "Eric", "c", "Clapton", "clapton@email.com", "pass", "123 4th st", "777777777", "Alumni");
INSERT INTO applications VALUES(77777777, "student", "F", "PhD", "Fall", 2020, "this is my experience", "this is my area of interest", "2023-04-20");
INSERT INTO student_classes VALUES(77777777, '1', '2023-1-1-1','B');
INSERT INTO student_classes VALUES(77777777, '3', '2023-1-3-1',  'B');
INSERT INTO student_classes VALUES(77777777, '2', '2023-1-2-1',  'B');
INSERT INTO student_classes VALUES(77777777, '5', '2023-1-5-1',  'B');
INSERT INTO student_classes VALUES(77777777, '6', '2023-1-6-1',  'B');
INSERT INTO student_classes VALUES(77777777, '7', '2023-1-7-1',  'B');
INSERT INTO student_classes VALUES(77777777, '8', '2023-1-8-1',  'B');
INSERT INTO student_classes VALUES(77777777, '14', '2023-1-14-1',  'A');
INSERT INTO student_classes VALUES(77777777, '15', '2023-1-15-1',  'A');
INSERT INTO student_classes VALUES(77777777, '16', '2023-1-16-1',  'A');
