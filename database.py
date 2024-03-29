#!/usr/bin/env python

#-----------------------------------------------------------------------
# database.py
# Author: Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
#-----------------------------------------------------------------------


import os
from sqlalchemy import create_engine, Column, Integer, String, Enum, ForeignKey, Float, Text
from sqlalchemy.orm import declarative_base, Session, sessionmaker, relationship
import user as usermod
#-----------------------------------------------------------------------

_DATABASE_URL = os.environ['DATABASE_URL']
_DATABASE_URL = _DATABASE_URL.replace('postgres://', 'postgresql://')

#-----------------------------------------------------------------------

# Create an engine to connect to database
_engine = create_engine(_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum('student', 'professor', name='user_roles'), nullable=False)
    name = Column(String, nullable=False)
    answers = relationship("Answer", back_populates="user")
    classes = relationship("Class", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="student")

class Class(Base):
    __tablename__ = 'classes'
    class_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    instructor_id = Column(String, ForeignKey('users.user_id'))
    total_sessions_planned = Column(Integer, default=0) 
    possible_scores = Column(Integer, default=0)
    enrollments = relationship("Enrollment", back_populates="class_")
    questions = relationship("Question", back_populates="class_")
    summaries = relationship("Summary", back_populates="class_")
    instructor = relationship("User")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    enrollment_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    class_id = Column(String, ForeignKey('classes.class_id'))
    sessions_attended = Column(Integer, default=0)
    score = Column(Float, default=0)
    student = relationship("User")
    class_ = relationship("Class")

class Question(Base):
    __tablename__ = 'questions'
    question_id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey('classes.class_id'))
    text = Column(Text, nullable=False)
    answers = relationship("Answer", back_populates="question")
    class_ = relationship("Class")

class Answer(Base):
    __tablename__ = 'answers'
    answer_id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey('questions.question_id'))
    user_id = Column(String, ForeignKey('users.user_id'))
    text = Column(Text, nullable=False) 
    question = relationship("Question")
    user = relationship("User")

class Summary(Base):
    __tablename__ = 'summaries'
    summary_id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey('classes.class_id'))
    text = Column(Text, nullable=False)  
    class_ = relationship("Class")

# Create the tables in the database
Base.metadata.create_all(_engine)

#-----------------------------------------------------------------------

def get_users(role):
    users = []
    with Session(_engine) as session:
        query = session.query(User).filter(User.role == role)
        table = query.all()
        for row in table:
            user = usermod.User(row.user_id, row.email, row.password_hash, row.role, row.name)
            users.append(user)
    return users

def get_classes(instructor_id):
    classes = []
    with Session(_engine) as session:
        query = session.query(Class).filter(Class.instructor_id == instructor_id)
        table = query.all()
        for row in table:
            class_info = {
                'class_id': row.class_id,
                'title': row.title,
                'instructor_id': row.instructor_id
            }
            classes.append(class_info)
    return classes

def get_enrollments(class_id):
    sessions = []
    return sessions

#-----------------------------------------------------------------------

# For testing:

# def _test():
#     #user1 = User(user_id='1', email='johndoe@princeton.edu', password_hash='password123', role='student', name='John Doe')
#     #user2 = User(user_id='2', email='janedoe@princeton.edu', password_hash='password321', role='student', name='Jane Doe')
#     #user3 = User(user_id='3', email='maryjane@princeton.edu', password_hash='spiderman', role='student', name='Mary Jane')
#     Session = sessionmaker(bind=_engine)
#     session = Session()
#     #session.add(user1)
#     #session.add(user2)
#     # session.add(user3)
#     session.query(User).delete()
#     session.commit()
#     session.close()
#     print("All rows deleted successfully.")
#     #print("Printing current users:")
#     #users = get_users('student')
#     #for user in users:
#     #    print(user.get_user_id())
#     #    print(user.get_email())
#     #    print(user.get_password_hash())
#     #    print(user.get_role())
#     #    print(user.get_name())
#     #    print()

# if __name__ == '__main__':
#     _test()




#-----------------------------------------------------------------------

# Code to delete all database data
    
#    # Connect to the database
#    conn = engine.connect()
#    
#    # Create a MetaData object
#    metadata = MetaData()
#    
#    # Reflect all tables from the database
#    metadata.reflect(bind=engine)
#    
#    # Drop tables in the correct order, considering dependencies
#    metadata.drop_all(engine)
#    
#    # Close the connection
#    conn.close()
#
#-----------------------------------------------------------------------