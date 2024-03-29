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


# def insert_question(question_text, answer_text):
#     db_session = SessionLocal()
#     try:
#         new_question = Question(question_text=question_text, answer_text=answer_text)

#         db_session.add(new_question)
#         db_session.commit()

#         print("Question added successfully.")
#         return True
#     except Exception as e:
#         db_session.rollback()
#         print(f"An error occurred: {e}")
#         return False
#     finally:
#         db_session.close()


# def fetch_all_questions():
#     db_session = SessionLocal()
#     try:
#         questions = db_session.query(Question).all()
#         questions_list = [
#             {
#                 "id": question.id,
#                 "question_text": question.question_text,
#                 "answer_text": question.answer_text,
#             }
#             for question in questions
#         ]

#         return questions_list
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return []
#     finally:
#         db_session.close()


# if __name__ == "__main__":
#     insert_user(
#         user_id="user101",
#         email="user101@example.com",
#         password_hash="hash1",
#         role="student",
#         name="Alice Wonderland",
#         score=88.5,
#     )
#     insert_user(
#         user_id="user102",
#         email="user102@example.com",
#         password_hash="hash2",
#         role="professor",
#         name="Bob Builder",
#         score=92.0,
#     )
#     insert_user(
#         user_id="user103",
#         email="user103@example.com",
#         password_hash="hash3",
#         role="student",
#         name="Charlie Brown",
#         score=75.0,
#     )
#     insert_user(
#         user_id="user104",
#         email="user104@example.com",
#         password_hash="hash4",
#         role="professor",
#         name="Dorothy Gale",
#         score=85.0,
#     )
#     insert_user(
#         user_id="user105",
#         email="user105@example.com",
#         password_hash="hash5",
#         role="student",
#         name="Edward Scissorhands",
#         score=90.0,
#     )

#     insert_question(
#         question_text="What is the capital of France?",
#         answer_text="Paris",
#     )
#     insert_question(
#         question_text="What is the highest mountain in the world?",
#         answer_text="Mount Everest",
#     )
#     insert_question(
#         question_text="Who wrote 'To Kill a Mockingbird'?",
#         answer_text="Harper Lee",
#     )
