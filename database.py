#!/usr/bin/env python

# -----------------------------------------------------------------------
# database.py
# Author: Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
# -----------------------------------------------------------------------
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Column,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# -----------------------------------------------------------------------
_DATABASE_URL = os.environ["DATABASE_URL"]
_DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://")


# -----------------------------------------------------------------------





# Create an engine to connect to database
_engine = create_engine(_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum("student", "professor", name="user_roles"), nullable=False)
    netid = Column(String, nullable=False)
    answers = relationship("Answer", back_populates="user")
    classes = relationship("Class", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")


class Class(Base):
    __tablename__ = "classes"
    class_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    instructor_id = Column(String, ForeignKey("users.user_id"))
    total_sessions_planned = Column(Integer, default=0)
    possible_scores = Column(Integer, default=0)
    enrollments = relationship("Enrollment", back_populates="class_")
    questions = relationship("Question", back_populates="class_")
    sessions = relationship("ClassSession", back_populates="class_")
    instructor = relationship("User")


class Enrollment(Base):
    __tablename__ = "enrollments"
    enrollment_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    class_id = Column(String, ForeignKey("classes.class_id"))
    sessions_attended = Column(Integer, default=0)
    score = Column(Float, default=0)
    student = relationship("User", back_populates="enrollments")
    class_ = relationship("Class", back_populates="enrollments")


class ClassSession(Base):
    __tablename__ = "class_sessions"
    session_id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey("classes.class_id"))
    start_time = Column(
        DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    end_time = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=False)
    attendances = relationship("Attendance", back_populates="class_session")
    class_ = relationship("Class", back_populates="sessions")


class Attendance(Base):
    __tablename__ = "attendances"
    attendance_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("class_sessions.session_id"))
    user_id = Column(String, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    class_session = relationship("ClassSession", back_populates="attendances")
    student = relationship("User", back_populates="attendances")


class Question(Base):
    __tablename__ = "questions"
    question_id = Column(String, primary_key=True)
    class_id = Column(String, ForeignKey("classes.class_id"))
    text = Column(Text, nullable=False)
    class_ = relationship("Class", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    summaries = relationship("Summary", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"
    answer_id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.question_id"))
    user_id = Column(String, ForeignKey("users.user_id"))
    text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="answers")
    user = relationship("User", back_populates="answers")


class Summary(Base):
    __tablename__ = "summaries"
    summary_id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.question_id"))
    text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="summaries")


# Assuming _engine is your SQLAlchemy engine instance:
Base.metadata.create_all(_engine)
# --------------------------------------------------------------------
