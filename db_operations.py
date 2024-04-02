import uuid
from sqlalchemy.exc import SQLAlchemyError
from database import Enrollment, SessionLocal, Student, Professor, Class


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
