# from sqlalchemy.orm import sessionmaker
# from models import engine, User, Class, Question

# SessionLocal = sessionmaker(bind=engine)

# def get_users(role):
#     """Fetch users based on their role (professor or student)."""
#     with SessionLocal() as session:
#         return session.query(User).filter(User.role == role).all()

# def add_user(user_id, email, password_hash, role, name):
#     """Add a new user to the database."""
#     with SessionLocal() as session:
#         user = User(user_id=user_id, email=email, password_hash=password_hash, role=role, name=name)
#         session.add(user)
#         session.commit()

# def add_question(class_id, text):
#     """Add a new question to a class."""
#     with SessionLocal() as session:
#         question = Question(class_id=class_id, text=text)
#         session.add(question)
#         session.commit()

# def delete_question(question_id):
#     """Delete a question based on its ID."""
#     with SessionLocal() as session:
#         question = session.query(Question).filter(Question.question_id == question_id).first()
#         if question:
#             session.delete(question)
#             session.commit()

# def get_classes(instructor_id):
#     """Fetch classes taught by a specific instructor."""
#     with SessionLocal() as session:
#         return session.query(Class).filter(Class.instructor_id == instructor_id).all()

# def update_user(user_id, **kwargs):
#     """Update a user's information based on the provided keyword arguments."""
#     with SessionLocal() as session:
#         user = session.query(User).filter(User.user_id == user_id).first()
#         if user:
#             for key, value in kwargs.items():
#                 setattr(user, key, value)
#             session.commit()

# def get_questions_by_class(class_id):
#     """Fetch all questions for a specific class."""
#     with SessionLocal() as session:
#         return session.query(Question).filter(Question.class_id == class_id).all()
