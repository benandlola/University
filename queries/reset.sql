-- recreate all tables, leaving no data
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
    user_type varchar(32),
    PRIMARY KEY(uid)
);

DROP TABLE IF EXISTS current_sections;
CREATE TABLE current_sections (
    cid INTEGER,
    section_id varchar(16),
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

DROP TABLE IF EXISTS student_classes;
CREATE TABLE student_classes (
    student_uid INTEGER,
    cid INTEGER,
    section_id varchar(16),
    grade char(4),
    finalized BOOL,
    PRIMARY KEY(student_uid, cid, section_id),
    FOREIGN KEY(student_uid) 
        REFERENCES users(uid),
    FOREIGN KEY(cid, section_id) 
        REFERENCES current_sections(cid, section_id)
);

SET FOREIGN_KEY_CHECKS=1;


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
-- sysadmin
INSERT INTO users VALUES ('00000000',"sysadmin","fakesalt","sysadmin","SU","super","fake address, Washington DC",'1900-10-10','sysadmin');
-- our teacehrs
INSERT INTO users VALUES ('10000000',"pass","fakesalt","teacher1","","one","fake address, Washington DC",'1900-10-10','faculty');
INSERT INTO users VALUES ('20000000',"pass","fakesalt","teacher2","","two","fake address, Washington DC",'1900-10-10','faculty');
INSERT INTO users VALUES ('30000000',"pass","fakesalt","teacher3","","three","fake address, Washington DC",'1900-10-10','faculty');
INSERT INTO users VALUES ('40000000',"pass","fakesalt","teacher4","","four","fake address, Washington DC",'1900-10-10','faculty');
-- required users
INSERT INTO users VALUES ('88888888',"test","fakesalt","Billie","","Holiday","fake address, Washington DC",'1900-10-10','student_m');
INSERT INTO users VALUES ('99999999',"test","fakesalt","Diana","","Krall","fake address, Washington DC",'1900-10-10','student_m');
INSERT INTO users VALUES ('50000000',"test","fakesalt","Narahari","","five","fake address, Washington DC",'1900-10-10','faculty');
INSERT INTO users VALUES ('60000000',"test","fakesalt","Choi","","six","fake address, Washington DC",'1900-10-10','faculty');
INSERT INTO users VALUES ('70000000',"test","fakesalt","gradsec","","seven","fake address, Washington DC",'1900-10-10','grad_sec');


-- add sections
INSERT INTO current_sections VALUES (1,'2023-1-1-1','10000000',2023,1,'M',1);
INSERT INTO current_sections VALUES (2,'2023-1-2-1','50000000',2023,1,'T',1);
INSERT INTO current_sections VALUES (3,'2023-1-3-1','60000000',2023,1,'W',1);
INSERT INTO current_sections VALUES (5,'2023-1-5-1','10000000',2023,1,'M',3);
INSERT INTO current_sections VALUES (6,'2023-1-6-1','10000000',2023,1,'T',3);
INSERT INTO current_sections VALUES (7,'2023-1-7-1','10000000',2023,1,'W',3);
INSERT INTO current_sections VALUES (8,'2023-1-8-1','10000000',2023,1,'R',3);
INSERT INTO current_sections VALUES (9,'2023-1-9-1','20000000',2023,1,'T',1);
INSERT INTO current_sections VALUES (11,'2023-1-11-1','20000000',2023,1,'M',3);
INSERT INTO current_sections VALUES (12,'2023-1-12-1','20000000',2023,1,'M',1);
INSERT INTO current_sections VALUES (10,'2023-1-10-1','20000000',2023,1,'R',3);
INSERT INTO current_sections VALUES (13,'2023-1-13-1','20000000',2023,1,'W',3);
INSERT INTO current_sections VALUES (14,'2023-1-14-1','20000000',2023,1,'T',3);
INSERT INTO current_sections VALUES (15,'2023-1-15-1','30000000',2023,1,'M',3);
INSERT INTO current_sections VALUES (16,'2023-1-16-1','30000000',2023,1,'W',3);
INSERT INTO current_sections VALUES (19,'2023-1-19-1','30000000',2023,1,'W',1);
INSERT INTO current_sections VALUES (20,'2023-1-20-1','40000000',2023,1,'M',3);
INSERT INTO current_sections VALUES (21,'2023-1-21-1','40000000',2023,1,'T',3);
INSERT INTO current_sections VALUES (22,'2023-1-22-1','40000000',2023,1,'W',3);
INSERT INTO current_sections VALUES (18,'2023-1-18-1','40000000',2023,1,'R',2);

-- 2023 2
INSERT INTO current_sections VALUES (1,'2023-2-1-1','10000000',2023,2,'M',1);
INSERT INTO current_sections VALUES (2,'2023-2-2-1','50000000',2023,2,'T',1);
INSERT INTO current_sections VALUES (3,'2023-2-3-1','60000000',2023,2,'W',1);
INSERT INTO current_sections VALUES (5,'2023-2-5-1','10000000',2023,2,'M',3);
INSERT INTO current_sections VALUES (6,'2023-2-6-1','10000000',2023,2,'T',3);
INSERT INTO current_sections VALUES (7,'2023-2-7-1','10000000',2023,2,'W',3);
INSERT INTO current_sections VALUES (8,'2023-2-8-1','10000000',2023,2,'R',3);
INSERT INTO current_sections VALUES (9,'2023-2-9-1','20000000',2023,2,'T',1);
INSERT INTO current_sections VALUES (11,'2023-2-11-1','20000000',2023,2,'M',3);
INSERT INTO current_sections VALUES (12,'2023-2-12-1','20000000',2023,2,'M',1);
INSERT INTO current_sections VALUES (10,'2023-2-10-1','20000000',2023,2,'R',3);
INSERT INTO current_sections VALUES (13,'2023-2-13-1','20000000',2023,2,'W',3);
INSERT INTO current_sections VALUES (14,'2023-2-14-1','20000000',2023,2,'T',3);
INSERT INTO current_sections VALUES (15,'2023-2-15-1','30000000',2023,2,'M',3);
INSERT INTO current_sections VALUES (16,'2023-2-16-1','30000000',2023,2,'W',3);
INSERT INTO current_sections VALUES (19,'2023-2-19-1','30000000',2023,2,'W',1);
INSERT INTO current_sections VALUES (20,'2023-2-20-1','40000000',2023,2,'M',3);
INSERT INTO current_sections VALUES (21,'2023-2-21-1','40000000',2023,2,'T',3);
INSERT INTO current_sections VALUES (22,'2023-2-22-1','40000000',2023,2,'W',3);
INSERT INTO current_sections VALUES (18,'2023-2-18-1','40000000',2023,2,'R',2);

-- 2023 3
INSERT INTO current_sections VALUES (1,'2023-3-1-1','10000000',2023,3,'M',1);
INSERT INTO current_sections VALUES (2,'2023-3-2-1','50000000',2023,3,'T',1);
INSERT INTO current_sections VALUES (3,'2023-3-3-1','60000000',2023,3,'W',1);
INSERT INTO current_sections VALUES (5,'2023-3-5-1','10000000',2023,3,'M',3);
INSERT INTO current_sections VALUES (6,'2023-3-6-1','10000000',2023,3,'T',3);
INSERT INTO current_sections VALUES (7,'2023-3-7-1','10000000',2023,3,'W',3);
INSERT INTO current_sections VALUES (8,'2023-3-8-1','10000000',2023,3,'R',3);
INSERT INTO current_sections VALUES (9,'2023-3-9-1','20000000',2023,3,'T',1);
INSERT INTO current_sections VALUES (11,'2023-3-11-1','20000000',2023,3,'M',3);
INSERT INTO current_sections VALUES (12,'2023-3-12-1','20000000',2023,3,'M',1);
INSERT INTO current_sections VALUES (10,'2023-3-10-1','20000000',2023,3,'R',3);
INSERT INTO current_sections VALUES (13,'2023-3-13-1','20000000',2023,3,'W',3);
INSERT INTO current_sections VALUES (14,'2023-3-14-1','20000000',2023,3,'T',3);
INSERT INTO current_sections VALUES (15,'2023-3-15-1','30000000',2023,3,'M',3);
INSERT INTO current_sections VALUES (16,'2023-3-16-1','30000000',2023,3,'W',3);
INSERT INTO current_sections VALUES (19,'2023-3-19-1','30000000',2023,3,'W',1);
INSERT INTO current_sections VALUES (20,'2023-3-20-1','40000000',2023,3,'M',3);
INSERT INTO current_sections VALUES (21,'2023-3-21-1','40000000',2023,3,'T',3);
INSERT INTO current_sections VALUES (22,'2023-3-22-1','40000000',2023,3,'W',3);
INSERT INTO current_sections VALUES (18,'2023-3-18-1','40000000',2023,3,'R',2);


-- 2024 1
INSERT INTO current_sections VALUES (1,'2024-1-1-1','10000000',2024,1,'M',1);
INSERT INTO current_sections VALUES (2,'2024-1-2-1','50000000',2024,1,'T',1);
INSERT INTO current_sections VALUES (3,'2024-1-3-1','60000000',2024,1,'W',1);
INSERT INTO current_sections VALUES (5,'2024-1-5-1','10000000',2024,1,'M',3);
INSERT INTO current_sections VALUES (6,'2024-1-6-1','10000000',2024,1,'T',3);
INSERT INTO current_sections VALUES (7,'2024-1-7-1','10000000',2024,1,'W',3);
INSERT INTO current_sections VALUES (8,'2024-1-8-1','10000000',2024,1,'R',3);
INSERT INTO current_sections VALUES (9,'2024-1-9-1','20000000',2024,1,'T',1);
INSERT INTO current_sections VALUES (11,'2024-1-11-1','20000000',2024,1,'M',3);
INSERT INTO current_sections VALUES (12,'2024-1-12-1','20000000',2024,1,'M',1);
INSERT INTO current_sections VALUES (10,'2024-1-10-1','20000000',2024,1,'R',3);
INSERT INTO current_sections VALUES (13,'2024-1-13-1','20000000',2024,1,'W',3);
INSERT INTO current_sections VALUES (14,'2024-1-14-1','20000000',2024,1,'T',3);
INSERT INTO current_sections VALUES (15,'2024-1-15-1','30000000',2024,1,'M',3);
INSERT INTO current_sections VALUES (16,'2024-1-16-1','30000000',2024,1,'W',3);
INSERT INTO current_sections VALUES (19,'2024-1-19-1','30000000',2024,1,'W',1);
INSERT INTO current_sections VALUES (20,'2024-1-20-1','40000000',2024,1,'M',3);
INSERT INTO current_sections VALUES (21,'2024-1-21-1','40000000',2024,1,'T',3);
INSERT INTO current_sections VALUES (22,'2024-1-22-1','40000000',2024,1,'W',3);
INSERT INTO current_sections VALUES (18,'2024-1-18-1','40000000',2024,1,'R',2);

-- 2024 2
INSERT INTO current_sections VALUES (1,'2024-2-1-1','10000000',2024,2,'M',1);
INSERT INTO current_sections VALUES (2,'2024-2-2-1','50000000',2024,2,'T',1);
INSERT INTO current_sections VALUES (3,'2024-2-3-1','60000000',2024,2,'W',1);
INSERT INTO current_sections VALUES (5,'2024-2-5-1','10000000',2024,2,'M',3);
INSERT INTO current_sections VALUES (6,'2024-2-6-1','10000000',2024,2,'T',3);
INSERT INTO current_sections VALUES (7,'2024-2-7-1','10000000',2024,2,'W',3);
INSERT INTO current_sections VALUES (8,'2024-2-8-1','10000000',2024,2,'R',3);
INSERT INTO current_sections VALUES (9,'2024-2-9-1','20000000',2024,2,'T',1);
INSERT INTO current_sections VALUES (11,'2024-2-11-1','20000000',2024,2,'M',3);
INSERT INTO current_sections VALUES (12,'2024-2-12-1','20000000',2024,2,'M',1);
INSERT INTO current_sections VALUES (10,'2024-2-10-1','20000000',2024,2,'R',3);
INSERT INTO current_sections VALUES (13,'2024-2-13-1','20000000',2024,2,'W',3);
INSERT INTO current_sections VALUES (14,'2024-2-14-1','20000000',2024,2,'T',3);
INSERT INTO current_sections VALUES (15,'2024-2-15-1','30000000',2024,2,'M',3);
INSERT INTO current_sections VALUES (16,'2024-2-16-1','30000000',2024,2,'W',3);
INSERT INTO current_sections VALUES (19,'2024-2-19-1','30000000',2024,2,'W',1);
INSERT INTO current_sections VALUES (20,'2024-2-20-1','40000000',2024,2,'M',3);
INSERT INTO current_sections VALUES (21,'2024-2-21-1','40000000',2024,2,'T',3);
INSERT INTO current_sections VALUES (22,'2024-2-22-1','40000000',2024,2,'W',3);
INSERT INTO current_sections VALUES (18,'2024-2-18-1','40000000',2024,2,'R',2);
-- 2024 3
INSERT INTO current_sections VALUES (1,'2024-3-1-1','10000000',2024,3,'M',1);
INSERT INTO current_sections VALUES (2,'2024-3-2-1','50000000',2024,3,'T',1);
INSERT INTO current_sections VALUES (3,'2024-3-3-1','60000000',2024,3,'W',1);
INSERT INTO current_sections VALUES (5,'2024-3-5-1','10000000',2024,3,'M',3);
INSERT INTO current_sections VALUES (6,'2024-3-6-1','10000000',2024,3,'T',3);
INSERT INTO current_sections VALUES (7,'2024-3-7-1','10000000',2024,3,'W',3);
INSERT INTO current_sections VALUES (8,'2024-3-8-1','10000000',2024,3,'R',3);
INSERT INTO current_sections VALUES (9,'2024-3-9-1','20000000',2024,3,'T',1);
INSERT INTO current_sections VALUES (11,'2024-3-11-1','20000000',2024,3,'M',3);
INSERT INTO current_sections VALUES (12,'2024-3-12-1','20000000',2024,3,'M',1);
INSERT INTO current_sections VALUES (10,'2024-3-10-1','20000000',2024,3,'R',3);
INSERT INTO current_sections VALUES (13,'2024-3-13-1','20000000',2024,3,'W',3);
INSERT INTO current_sections VALUES (14,'2024-3-14-1','20000000',2024,3,'T',3);
INSERT INTO current_sections VALUES (15,'2024-3-15-1','30000000',2024,3,'M',3);
INSERT INTO current_sections VALUES (16,'2024-3-16-1','30000000',2024,3,'W',3);
INSERT INTO current_sections VALUES (19,'2024-3-19-1','30000000',2024,3,'W',1);
INSERT INTO current_sections VALUES (20,'2024-3-20-1','40000000',2024,3,'M',3);
INSERT INTO current_sections VALUES (21,'2024-3-21-1','40000000',2024,3,'T',3);
INSERT INTO current_sections VALUES (22,'2024-3-22-1','40000000',2024,3,'W',3);
INSERT INTO current_sections VALUES (18,'2024-3-18-1','40000000',2024,3,'R',2);


-- add required student to there classes
INSERT INTO student_classes VALUES (88888888,'2','2023-3-2-1','IP',0);
INSERT INTO student_classes VALUES (88888888,'3','2023-3-3-1','IP',0);