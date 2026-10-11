---------------------------------------------------------
-- DROP OLD TABLES + SEQUENCE SAFELY
---------------------------------------------------------
BEGIN EXECUTE IMMEDIATE 'DROP TABLE attendance CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE results CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE courses CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE departments CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE students CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE users CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE seq_users_id'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

---------------------------------------------------------
-- CREATE TABLES
---------------------------------------------------------

CREATE TABLE students (
    roll_no        VARCHAR2(20) PRIMARY KEY,
    first_name     VARCHAR2(50) NOT NULL,
    last_name      VARCHAR2(50) NOT NULL,
    gender         VARCHAR2(10),
    date_of_birth  DATE,
    email          VARCHAR2(100),
    phone          VARCHAR2(20),
    address        VARCHAR2(200),
    department     VARCHAR2(50),
    semester       NUMBER
);

CREATE TABLE departments (
    dept_id    VARCHAR2(10) PRIMARY KEY,
    dept_name  VARCHAR2(50),
    hod_name   VARCHAR2(50),
    hod_email  VARCHAR2(100)
);

CREATE TABLE courses (
    course_id    VARCHAR2(10) PRIMARY KEY,
    course_name  VARCHAR2(100),
    credits      NUMBER,
    description  VARCHAR2(200)
);

CREATE TABLE results (
    roll_no   VARCHAR2(20),
    course    VARCHAR2(100),
    grade     VARCHAR2(5),
    remarks   VARCHAR2(200),
    CONSTRAINT fk_results_student FOREIGN KEY (roll_no) REFERENCES students(roll_no)
);

CREATE TABLE attendance (
    roll_no             VARCHAR2(20),
    course              VARCHAR2(100),
    attendance_percent  NUMBER,
    present_days        NUMBER,
    total_days          NUMBER,
    CONSTRAINT fk_attendance_student FOREIGN KEY (roll_no) REFERENCES students(roll_no)
);

CREATE TABLE users (
    user_id   NUMBER PRIMARY KEY,
    username  VARCHAR2(50) NOT NULL,
    password  VARCHAR2(100) NOT NULL,
    role      VARCHAR2(20) DEFAULT 'user'
);

---------------------------------------------------------
-- SEQUENCE + TRIGGER FOR AUTO-INCREMENT user_id
---------------------------------------------------------
CREATE SEQUENCE seq_users_id START WITH 1 INCREMENT BY 1;

CREATE OR REPLACE TRIGGER trg_users_id
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
   IF :NEW.user_id IS NULL THEN
      SELECT seq_users_id.NEXTVAL INTO :NEW.user_id FROM dual;
   END IF;
END;
/

---------------------------------------------------------
-- SAMPLE DATA INSERTS
---------------------------------------------------------

INSERT INTO students VALUES ('2025-CS-01','Hafsa','Ashraf','Female',DATE '2002-05-15',
 'hafsa@example.com','03001234567','Chishtian, Punjab','Computer Science',5);

INSERT INTO students VALUES ('2025-CS-02','Ali','Khan','Male',DATE '2001-08-20',
 'ali.khan@example.com','03007654321','Lahore, Punjab','Computer Science',3);

INSERT INTO departments VALUES ('D01','Computer Science','Dr. Ali Khan','ali.khan@uni.edu');
INSERT INTO departments VALUES ('D02','IT','Dr. Sara','sara@uni.edu');

INSERT INTO courses VALUES ('C01','Database Systems',3,'Covers relational DBMS, SQL, normalization');
INSERT INTO courses VALUES ('C02','Python Programming',4,'Covers Python basics, OOP, GUI, DB integration');

INSERT INTO results VALUES ('2025-CS-01','Database Systems','A','Excellent performance');
INSERT INTO results VALUES ('2025-CS-02','Python Programming','B+','Good, needs improvement in projects');

INSERT INTO attendance VALUES ('2025-CS-01','Database Systems',90,45,50);
INSERT INTO attendance VALUES ('2025-CS-02','Python Programming',85,34,40);

INSERT INTO users (username,password,role) VALUES ('admin','admin123','admin');
INSERT INTO users (username,password,role) VALUES ('teacher','teach123','teacher');
INSERT INTO users (username,password,role) VALUES ('student','stud123','student');

---------------------------------------------------------
-- SAVE CHANGES
---------------------------------------------------------
COMMIT;
