# from sqlalchemy import create_engine, Column, Integer, String, Enum, Float, Text
# from sqlalchemy.orm import declarative_base, relationship, sessionmaker
# import os

# _DATABASE_URL = os.environ['DATABASE_URL']
# _DATABASE_URL = _DATABASE_URL.replace('postgres://', 'postgresql://')

# engine = create_engine(_DATABASE_URL)
# Base = declarative_base()
# SessionLocal = sessionmaker(bind=engine)


# class User(Base):
#     __tablename__ = 'users'
#     user_id = Column(String, primary_key=True)
#     email = Column(String, unique=True, nullable=False)
#     password_hash = Column(String, nullable=False)
#     role = Column(Enum('student', 'professor', name='user_roles'), nullable=False)
#     name = Column(String, nullable=False)
#     score = Column(Float, nullable=True)
    
    
# class Question(Base):
#     __tablename__ = 'questions'
#     id = Column(Integer, primary_key=True)  
#     question_text = Column(Text, nullable=False)  
#     answer_text = Column(Text, nullable=False)  

    
# Base.metadata.create_all(engine)


# # class User(Base):
# #     __tablename__ = 'users'
# #     user_id = Column(String, primary_key=True)
# #     email = Column(String, unique=True, nullable=False)
# #     password_hash = Column(String, nullable=False)
# #     role = Column(Enum('student', 'professor', name='user_roles'), nullable=False)
# #     name = Column(String, nullable=False)
# #     answers = relationship("Answer", back_populates="user")
# #     classes = relationship("Class", back_populates="instructor")
# #     enrollments = relationship("Enrollment", back_populates="student")

# # class Class(Base):
# #     __tablename__ = 'classes'
# #     class_id = Column(String, primary_key=True)
# #     title = Column(String, nullable=False)
# #     instructor_id = Column(String, ForeignKey('users.user_id'))
# #     total_sessions_planned = Column(Integer, default=0)
# #     possible_scores = Column(Integer, default=0)
# #     enrollments = relationship("Enrollment", back_populates="class_")
# #     questions = relationship("Question", back_populates="class_")
# #     summaries = relationship("Summary", back_populates="class_")
# #     instructor = relationship("User", back_populates="classes")

# # class Enrollment(Base):
# #     __tablename__ = 'enrollments'
# #     enrollment_id = Column(String, primary_key=True)
# #     user_id = Column(String, ForeignKey('users.user_id'))
# #     class_id = Column(String, ForeignKey('classes.class_id'))
# #     sessions_attended = Column(Integer, default=0)
# #     score = Column(Float, default=0.0)
# #     student = relationship("User", back_populates="enrollments")
# #     class_ = relationship("Class", back_populates="enrollments")

# # class Question(Base):
# #     __tablename__ = 'questions'
# #     question_id = Column(String, primary_key=True)
# #     class_id = Column(String, ForeignKey('classes.class_id'))
# #     text = Column(Text, nullable=False)
# #     answers = relationship("Answer", back_populates="question")
# #     class_ = relationship("Class", back_populates="questions")
# #     summaries = relationship("Summary", back_populates="question")  

# # class Summary(Base):
# #     __tablename__ = 'summaries'
# #     summary_id = Column(String, primary_key=True)
# #     question_id = Column(String, ForeignKey('questions.question_id')) 
# #     text = Column(Text, nullable=False)
# #     question = relationship("Question", back_populates="summaries") 
# #     class_ = relationship("Class", back_populates="summaries")


# # class Answer(Base):
# #     __tablename__ = 'answers'
# #     answer_id = Column(String, primary_key=True)
# #     question_id = Column(String, ForeignKey('questions.question_id'))
# #     user_id = Column(String, ForeignKey('users.user_id'))
# #     text = Column(Text, nullable=False)
# #     question = relationship("Question", back_populates="answers")
# #     user = relationship("User", back_populates="answers")


