SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS classes;
CREATE TABLE classes (
    cid INTEGER,
    dept varchar(8),
    class_number INTEGER,
    title varchar(32),
    credit_hours INTEGER,
    PRIMARY KEY(cid)
);

DROP TABLE IF EXISTS current_sections;
CREATE TABLE current_sections (
    cid INTEGER,
    section_id varchar(8),
    professor_uid INTEGER,
    year INTEGER,
    semester INTEGER,
    day char(1),
    timeslot INTEGER,
    PRIMARY KEY(cid, section_id),
    FOREIGN KEY(cid) 
        REFERENCES classes(cid),
    FOREIGN KEY(professor_uid)
        REFERENCES users(uid)
);

DROP TABLE IF EXISTS prerequisites;
CREATE TABLE prerequisites (
    class_cid INTEGER,
    prereq_cid INTEGER,
    PRIMARY KEY(class_cid, prereq_cid),
    FOREIGN KEY(class_cid) 
        REFERENCES classes(cid),
    FOREIGN KEY(prereq_cid) 
        REFERENCES classes(cid)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uid INTEGER,
    password_hash CHAR(64),
    salt CHAR(16),
    first_name varchar(32),
    middle_initial varchar(4),
    last_name varchar(32),
    address varchar(64),
    birthday DATE,
    user_type INTEGER,
    PRIMARY KEY(uid)
);

DROP TABLE IF EXISTS student_classes;
CREATE TABLE student_classes (
    student_uid INTEGER,
    cid INTEGER,
    section_id varchar(8),
    grade char(4),
    finalized BOOL,
    PRIMARY KEY(student_uid, cid, section_id),
    FOREIGN KEY(student_uid) 
        REFERENCES users(uid),
    FOREIGN KEY(cid, section_id) 
        REFERENCES current_sections(cid, section_id)
);

SET FOREIGN_KEY_CHECKS=1;
