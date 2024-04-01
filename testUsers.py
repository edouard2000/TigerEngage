# user_operations.py
from typing import List
from database import User
from database import SessionLocal


def insert_user(user_id, email, password_hash, role, name, score=None):
    db_session = SessionLocal()
    existing_user = db_session.query(User).filter_by(user_id=user_id).first()
    if existing_user is None:
        new_user = User(
            user_id=user_id,
            email=email,
            password_hash=password_hash,
            role=role,
            name=name,
            score=score,
        )
        db_session.add(new_user)
        try:
            db_session.commit()
            print(f"User {email} added successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            db_session.rollback()
        finally:
            db_session.close()
    else:
        print(f"User with user_id {user_id} already exists.")


def fetch_all_users() -> List[User]:
    db_session = SessionLocal()
    users = db_session.query(User).all()
    print("Fetched users:", users)
    db_session.close()
    return users

