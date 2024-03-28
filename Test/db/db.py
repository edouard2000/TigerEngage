from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://user:password@localhost/tigerengage')
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum('student', 'professor', 'preceptor', name='user_roles'), nullable=False)
    name = Column(String, nullable=False)
    answers = relationship("Answer", back_populates="user")

class Class(Base):
    __tablename__ = 'classes'
    class_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey('users.user_id'))
    total_sessions_planned = Column(Integer, default=0) 
    posible_scores = Column(Integer, default=0)
    enrollments = relationship("Enrollment", back_populates="class_")
    questions = relationship("Question", back_populates="class_")
    summaries = relationship("Summary", back_populates="class_")
    instructor = relationship("User", back_populates="classes")

User.classes = relationship("Class", back_populates="instructor")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    enrollment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    class_id = Column(Integer, ForeignKey('classes.class_id'))
    sessions_attended = Column(Integer, default=0)
    score = Column(Float, default=0)

    user = relationship("User", back_populates="enrollments")
    class_ = relationship("Class", back_populates="enrollments")

class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.class_id'))
    text = Column(Text, nullable=False)

    answers = relationship("Answer", back_populates="question")
    class_ = relationship("Class", back_populates="questions")

class Answer(Base):
    __tablename__ = 'answers'
    answer_id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.question_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    text = Column(Text, nullable=False) 
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")

class Summary(Base):
    __tablename__ = 'summaries'
    summary_id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('classes.class_id'))
    text = Column(Text, nullable=False)  
    class_ = relationship("Class", back_populates="summaries")
