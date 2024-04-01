# Fucntion to create a users ( student or professor)
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal, Student, Professor


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
