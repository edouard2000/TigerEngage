#!/usr/bin/env python

# -----------------------------------------------------------------------
# database.py
# Author: Edouard KWIZERA and Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
# -----------------------------------------------------------------------

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, backref
from sqlalchemy import (
    create_engine,
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Boolean,
    Text,
)

# Database URL and engine setup
_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage",
)
_DATABASE_URL = _DATABASE_URL.replace("postgres://", "postgresql://")
_engine = create_engine(_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Base = declarative_base()


# -----------------------------------------------------------------------


class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String(50))

    messages = relationship(
        "ChatMessage", back_populates="sender", order_by="ChatMessage.timestamp"
    )

    __mapper_args__ = {"polymorphic_identity": "user", "polymorphic_on": role}


class Student(User):
    __tablename__ = "students"
    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)
    enrollments = relationship("Enrollment", back_populates="student")
    attendances = relationship("Attendance", back_populates="student")
    answers = relationship("Answer", back_populates="user")

    __mapper_args__ = {
        "polymorphic_identity": "student",
    }


class Professor(User):
    __tablename__ = "professors"
    user_id = Column(String, ForeignKey("users.user_id"), primary_key=True)
    classes = relationship("Class", back_populates="instructor")

    __mapper_args__ = {
        "polymorphic_identity": "professor",
    }


class Class(Base):
    __tablename__ = "classes"
    class_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    instructor_id = Column(String, ForeignKey("professors.user_id"))
    total_sessions_planned = Column(Integer, default=0)
    possible_scores = Column(Integer, default=0)
    instructor = relationship("Professor", back_populates="classes")
    enrollments = relationship("Enrollment", back_populates="class_")
    sessions = relationship("ClassSession", back_populates="class_")
    questions = relationship("Question", back_populates="class_")
    messages = relationship(
        "ChatMessage", back_populates="class_", order_by="ChatMessage.timestamp"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"
    enrollment_id = Column(String, primary_key=True)
    student_id = Column(String, ForeignKey("students.user_id"))
    class_id = Column(String, ForeignKey("classes.class_id"))
    sessions_attended = Column(Integer, default=0)
    score = Column(Integer, default=0)
    is_ta = Column(Boolean, default=False)
    student = relationship("Student", back_populates="enrollments")
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
    ended = Column(Boolean, default=False)
    class_ = relationship("Class", back_populates="sessions")
    attendances = relationship("Attendance", back_populates="class_session")
    messages = relationship(
        "ChatMessage",
        back_populates="session",
        order_by="ChatMessage.timestamp",
        cascade="all, delete",
    )


class Attendance(Base):
    __tablename__ = "attendances"
    attendance_id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("class_sessions.session_id"))
    student_id = Column(String, ForeignKey("students.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    class_session = relationship("ClassSession", back_populates="attendances")
    student = relationship("Student", back_populates="attendances")


class Question(Base):
    __tablename__ = "questions"
    question_id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    class_id = Column(String, ForeignKey("classes.class_id"))
    text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
    is_displayed = Column(Boolean, default=False, nullable=False)
    class_ = relationship("Class", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
    summaries = relationship("Summary", back_populates="question")


class Answer(Base):
    __tablename__ = "answers"
    answer_id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.question_id"))
    student_id = Column(String, ForeignKey("students.user_id"))
    text = Column(Text, nullable=False)
    question = relationship("Question", back_populates="answers")
    user = relationship("Student", back_populates="answers")


class Summary(Base):
    __tablename__ = "summaries"
    summary_id = Column(String, primary_key=True)
    question_id = Column(String, ForeignKey("questions.question_id"))
    text = Column(Text, nullable=False)
    notes = Column(Text, nullable=False)
    question = relationship("Question", back_populates="summaries")


class AfterClassInputs(Base):
    __tablename__ = "after_class_inputs"
    input_id = Column(String, primary_key=True)
    class_session_id = Column(String, ForeignKey("class_sessions.session_id"))
    class_id = Column(String, ForeignKey("classes.class_id"))
    student_id = Column(String, ForeignKey("students.user_id"))
    response_category = Column(String, nullable=False)
    comment = Column(Text, nullable=True)
    class_session = relationship("ClassSession", back_populates="feedbacks")
    class_ = relationship("Class", back_populates="feedbacks")
    student = relationship("Student", back_populates="feedbacks")


ClassSession.feedbacks = relationship(
    "AfterClassInputs", back_populates="class_session"
)
Class.feedbacks = relationship("AfterClassInputs", back_populates="class_")
Student.feedbacks = relationship("AfterClassInputs", back_populates="student")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    message_id = Column(String, primary_key=True)
    sender_id = Column(String, ForeignKey("users.user_id"))
    class_id = Column(String, ForeignKey("classes.class_id"))
    session_id = Column(String, ForeignKey("class_sessions.session_id"))
    text = Column(Text, nullable=False)
    role = Column(String(50))
    timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("UTC"))
    )
    replied_to_id = Column(
        String, ForeignKey("chat_messages.message_id"), nullable=True
    )

    # Relationships
    sender = relationship("User", back_populates="messages")
    class_ = relationship("Class", back_populates="messages")
    session = relationship("ClassSession", back_populates="messages")
    replies = relationship(
        "ChatMessage", backref=backref("replied_to", remote_side=[message_id])
    )


# Base.metadata.drop_all(_engine)
Base.metadata.create_all(_engine)
