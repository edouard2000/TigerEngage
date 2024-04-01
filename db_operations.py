
import uuid
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal, Student, Professor, Class, User

def create_user(netid, role):
    """
    Creates a new user with the specified netID and role. Adjusted to handle
    separate models or roles for students and professors.
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
    Checks if a user with the specified user_id already exists in either the Student or Professor tables in the database.
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
