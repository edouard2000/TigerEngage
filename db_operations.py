#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_operations.py
# Author: Edouard KWIZERA and Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
# -----------------------------------------------------------------------


import uuid
from sqlalchemy.exc import SQLAlchemyError
from database import Enrollment, Question, SessionLocal, Student, Professor, Class, User


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
            return True
        except SQLAlchemyError as e:
            print(f"Error adding class to database: {e}")
            session.rollback()
            return False


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
    Retrieves a list of classes a student is enrolled in by their netID.
    Args:
        netid (str): The netID of the student.
    Returns:
        list: A list of Class objects the student is enrolled in.
    """
    with SessionLocal() as db_session:
        student = db_session.query(Student).filter(Student.netid == netid).first()
        if not student:
            return []
        enrolled_classes = [enrollment.class_ for enrollment in student.enrollments]
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


def computer_precentage_score(score, possible_scores):
    """Adjusted to ensure string return with '%'."""
    if possible_scores == 0:
        return "0%"
    else:
        return str(int((score / possible_scores) * 100)) + "%"


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
  
    new_enrollment = Enrollment(student_id=user_id, class_id=class_id)
    db.session.add(new_enrollment)
    try:
        db.session.commit()
        return True
    except Exception as e:
        print(f"Enrollment error: {e}")
        db.session.rollback()
        return False