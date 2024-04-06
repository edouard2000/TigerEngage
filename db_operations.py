#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_operations.py
# Author: Edouard Kwizera and Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
# -----------------------------------------------------------------------

from datetime import datetime
import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from database import (
    Enrollment,
    Question,
    SessionLocal,
    Student,
    Professor,
    Class,
    User,
    ClassSession,
    Attendance,
)


def create_user(netid, role):
    """
    Creates a new user as either a Student or Professor based on the role.
    """
    with SessionLocal() as session:
        email = f"{netid}@princeton.edu"
        if role == "student":
            new_user = Student(user_id=netid, email=email, netid=netid)
        elif role == "professor":
            new_user = Professor(user_id=netid, email=email, netid=netid)
        else:
            print(f"Invalid role: {role}")
            return False

        session.add(new_user)
        try:
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Error adding user to database: {e}")
            session.rollback()
            return False


def create_class_for_professor(netid, title):
    """
    Creates a new class associated with the specified professor's netID.
    """
    with SessionLocal() as session:

        professor = session.query(Professor).filter_by(user_id=netid).first()
        if not professor:
            print(f"No professor found with netID: {netid}")
            return False

        new_class = Class(
            class_id=str(uuid.uuid4()),
            title=title,
            instructor_id=netid,
            total_sessions_planned=0,
            possible_scores=0,
        )
        session.add(new_class)
        try:
            session.commit()
            print(f"Class '{title}' successfully created by Professor {netid}.")
            return True, new_class.class_id
        except SQLAlchemyError as e:
            print(f"Error adding class to database: {e}")
            session.rollback()
            return False, None


def user_exists(user_id):
    """
    Checks if a user with the specified user_id already exists
    in either the Student or Professor tables in the database.

    Args:
        user_id (str): The ID of the user.
    """
    with SessionLocal() as session:
        student = session.query(Student).filter_by(user_id=user_id).first()
        professor = session.query(Professor).filter_by(user_id=user_id).first()
        return student is not None or professor is not None


def has_classes(professor_id):
    """
    Checks if a professor with the specified professor_id has any associated classes.
    Args:
        professor_id (str): The ID of the professor.
    Returns:
        bool: True if the professor has one or more classes, False otherwise.
    """
    with SessionLocal() as session:
        class_count = session.query(Class).filter_by(instructor_id=professor_id).count()
        return class_count > 0


def get_student_classes(netid: str) -> list:
    """
    Retrieves a list of classes a student is enrolled in by their netID, including the instructor data and the active session status.
    Args:
        netid (str): The netID of the student.
    Returns:
        list: A list of Class objects the student is enrolled in, including the instructor and active session status.
    """
    with SessionLocal() as db_session:
        student = (
            db_session.query(Student)
            .options(
                joinedload(Student.enrollments)
                .joinedload(Enrollment.class_)
                .joinedload(Class.instructor)
            )
            .filter(Student.netid == netid)
            .first()
        )
        if not student:
            return []
        enrolled_classes = [
            {
                "id": enrollment.class_.class_id,
                "name": enrollment.class_.title,
                "instructor": enrollment.class_.instructor.user_id,
                "is_active": db_session.query(ClassSession).filter_by(class_id=enrollment.class_.class_id, is_active=True).count() > 0
            }
            for enrollment in student.enrollments
            if enrollment.class_
        ]
        return enrolled_classes



def get_students_for_class(class_id: str):
    """
    Retrieves all students enrolled in a specific class.
    """
    with SessionLocal() as session:
        students = (
            session.query(Student)
            .join(Enrollment)
            .filter(Enrollment.class_id == class_id)
            .all()
        )
        return students


def get_student_score_and_possible_for_class(user_id: str, class_id: str):
    """
    Retrieves the score of a specific student for a specific class and the possible score for that class.
    Args:
        student_id (str): The student's user ID.
        class_id (str): The class ID.
    Returns:
        tuple: A tuple containing the student's score and the possible score for the class.
               Returns (None, None) if the enrollment or class doesn't exist.
    """
    with SessionLocal() as session:
        enrollment = (
            session.query(Enrollment)
            .filter_by(user_id=user_id, class_id=class_id)
            .first()
        )
        class_info = session.query(Class).filter_by(class_id=class_id).first()

        if enrollment and class_info:
            return (enrollment.score, class_info.possible_scores)
        return (None, None)


def compute_percentage_score(score, possible_scores):
    if possible_scores > 0:
        return "{:.2f}%".format((score / possible_scores) * 100)
    else:
        return "N/A"



def get_professor_class(netid: str) -> str:
    """
    Retrieves the name of the class associated with a specific professor by their netID.
    Args:
        netid (str): The netID of the professor.
    Returns:
        str: The name of the class associated with the professor, or None if no class is found.
    """
    with SessionLocal() as session:
        professor_class = (
            session.query(Class.title)
            .join(Professor, Professor.user_id == Class.instructor_id)
            .filter(Professor.netid == netid)
            .first()
        )
        if professor_class:
            return professor_class.title
        else:
            return None


def get_user_role(username):
    """
    Queries the database for the user's role based on their username.
    Args:
        username (str): The username of the user.
    Returns:
        str: The role of the user (e.g., 'student', 'professor') or None if not found.
    """
    with SessionLocal() as session:
        user = session.query(User).filter_by(netid=username).first()
        if user:
            return user.role
        return None


def add_question_to_class(
    class_id: str, question_text: str, correct_answer: str
) -> bool:
    """
    Adds a question and its correct answer to a class.

    Args:
        class_id (str): The unique identifier for the class.
        question_text (str): The text of the question to be added.
        correct_answer (str): The correct answer to the question.

    Returns:
        bool: True if the question was successfully added, False otherwise.
    """
    with SessionLocal() as session:
        new_question = Question(
            question_id=str(uuid.uuid4()),
            class_id=class_id,
            text=question_text,
            correct_answer=correct_answer,
        )
        session.add(new_question)
        try:
            session.commit()
            print(f"Question added to class {class_id}.")
            return True
        except SQLAlchemyError as e:
            print(f"Failed to add question to class {class_id}: {e}")
            session.rollback()
            return False


def get_professors_class_id(user_id):
    session = SessionLocal()
    try:
        professor_classes = (
            session.query(Class)
            .join(Professor, Class.instructor_id == Professor.user_id)
            .filter(Professor.user_id == user_id)
            .first()
        )
        if professor_classes:
            return professor_classes.class_id
        else:
            return None
    except Exception as e:
        print(f"Error fetching professor's class_id: {e}")
        return None
    finally:
        session.close()


def get_questions_for_class(class_id: str):
    """
    Retrieves questions for a specific class.

    Args:
        class_id (str): The unique identifier for the class.

    Returns:
        list: A list of dictionaries, each containing the question ID, text, and correct answer.
    """
    with SessionLocal() as session:
        questions = session.query(Question).filter_by(class_id=class_id).all()
        questions_data = [
            {
                "question_id": question.question_id,
                "text": question.text,
                "correct_answer": question.correct_answer,
            }
            for question in questions
        ]
        return questions_data


def enroll_student(user_id, class_id):
    with SessionLocal() as session:
        new_enrollment = Enrollment(
            enrollment_id=str(uuid.uuid4()), 
            student_id=user_id, 
            class_id=class_id
        )
        session.add(new_enrollment)
        try:
            session.commit()
            print(f"Student {user_id} successfully enrolled in class {class_id}.")
            return True
        except Exception as e:
            print(f"Enrollment error: {e}")
            session.rollback()
            return False



def is_instructor_for_class(username, class_id):
    with SessionLocal() as db:
        instructor = (
            db.query(User)
            .filter(User.netid == username, User.role == "professor")
            .first()
        )
        class_ = db.query(Class).filter_by(class_id=class_id).first()

        if instructor and class_ and class_.instructor_id == instructor.user_id:
            return True
        else:
            return False


def get_active_session_for_class(class_id):
    with SessionLocal() as db:
        active_session = (
            db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        )
        return active_session


def start_new_session(class_id):
    with SessionLocal() as db:
        new_session = ClassSession(
            session_id=str(uuid.uuid4()),
            class_id=class_id,
            start_time=datetime.now(),
            is_active=True,
        )
        db.add(new_session)
        try:
            db.commit()
            print(
                f"Session {new_session.session_id} for class {class_id} started at {new_session.start_time}"
            )
            return new_session
        except Exception as e:
            db.rollback()
            print(e)
            return None


def has_checked_in(username, session_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.netid == username).first()
        if not user:
            return False
        attendance_record = (
            db.query(Attendance)
            .filter_by(student_id=user.user_id, session_id=session_id)
            .first()
        )

        return attendance_record is not None


def record_attendance(username, class_id, session_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.netid == username).first()
        if not user:
            return False

        class_session = (
            db.query(ClassSession)
            .filter_by(session_id=session_id, class_id=class_id, is_active=True)
            .first()
        )
        if not class_session:
            return False

        if has_checked_in(username, session_id):
            return False

        new_attendance = Attendance(
            attendance_id=str(uuid.uuid4()), 
            session_id=session_id, 
            student_id=user.user_id, 
            timestamp=datetime.now()
        )
        db.add(new_attendance)
        try:
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(e)
            return False



def is_student_enrolled_in_class(username, class_id):
    """
    Check if the student identified by the username is enrolled in the class specified by class_id.

    Args:
        username (str): The username (netID) of the student.
        class_id (str): The ID of the class.

    Returns:
        bool: True if the student is enrolled in the class, False otherwise.
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.netid == username).first()
        if not user:
            return False
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user.user_id, class_id=class_id)
            .first()
        )
        return enrollment is not None
    
    
    
    
def update_question_status(question_id, class_id, is_active):
    session = SessionLocal()
    try:
        question = session.query(Question).filter_by(question_id=question_id, class_id=class_id).first()
        if question:
            question.is_active = is_active 
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to update question status: {e}")
        session.rollback()
        return False
    finally:
        session.close()


# if __name__ == '__main__':

#     professors_classes = [
#     {"netid": "prof1", "class_title": "Introduction to Computer Science"},
#     {"netid": "prof2", "class_title": "Advanced Mathematics"},
#     {"netid": "prof3", "class_title": "Modern Physics"},
#     {"netid": "prof4", "class_title": "Literature 101"},
#     {"netid": "prof5", "class_title": "World History"},
# ]

#     for professor in professors_classes:
#         # Create professor user
#         user_created = create_user(professor['netid'], 'professor')
#         if user_created:
#             print(f"Professor {professor['netid']} created successfully.")
#         else:
#             print(f"Failed to create professor {professor['netid']}.")

#         # Create class for professor
#         class_created, class_id = create_class_for_professor(professor['netid'], professor['class_title'])
#         if class_created:
#             print(f"Class '{professor['class_title']}' created for Professor {professor['netid']}. Class ID: {class_id}")
#         else:
#             print(f"Failed to create class '{professor['class_title']}' for Professor {professor['netid']}.")
