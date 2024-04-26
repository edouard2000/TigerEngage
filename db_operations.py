#!/usr/bin/env python

# -----------------------------------------------------------------------
# db_operations.py
# Author: Edouard Kwizera and Jourdain Babisa
# External Database URL: postgres://tigerengage_user:CcchdFt18gGxz2a2dwMFdMBsxh20FcG6@dpg-cnvo5ldjm4es73drsoeg-a.ohio-postgres.render.com/tigerengage
# -----------------------------------------------------------------------

from datetime import datetime
import uuid
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from database import (
    Enrollment,
    Question,
    SessionLocal,
    Student,
    Professor,
    Class,
    Summary,
    User,
    ClassSession,
    Attendance,
    Answer,
)
from summarizer import TextSummarizer
from req_lib import ReqLib


def create_user(netid, role):
    """
    Creates a new user as either a Student or Professor based on the role.
    """
    with SessionLocal() as session:
        email = f"{netid}@princeton.edu"
        req_lib = ReqLib()
        name = req_lib.getJSON(req_lib.configs.USERS, uid=netid,)
        name = name[0].get('displayname')
        if role == "student":
            new_user = Student(user_id=netid, email=email, name=name)
        elif role == "professor":
            new_user = Professor(user_id=netid, email=email, name=name)
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
            return True, new_class.class_id
        except SQLAlchemyError as e:
            print(f"Error adding class to database: {e}")
            session.rollback()
            return False, None


def user_exists(user_id):
    """
    Checks if a user with the specified user_id already exists
    in either the Student or Professor tables in the database.

    Args:
        user_id (str): The ID of the user.
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
    Retrieves a list of classes a student is enrolled in by their netID, including the instructor data and the active session status.
    Args:
        netid (str): The netID of the student.
    Returns:
        list: A list of Class objects the student is enrolled in, including the instructor and active session status.
    """
    with SessionLocal() as db_session:
        student = (
            db_session.query(Student)
            .options(
                joinedload(Student.enrollments)
                .joinedload(Enrollment.class_)
                .joinedload(Class.instructor)
            )
            .filter(Student.user_id == netid)
            .first()
        )
        if not student:
            return []
        enrolled_classes = [
            {
                "id": enrollment.class_.class_id,
                "name": enrollment.class_.title,
                "instructor": enrollment.class_.instructor.user_id,
                "is_active": db_session.query(ClassSession)
                .filter_by(class_id=enrollment.class_.class_id, is_active=True)
                .count()
                > 0,
            }
            for enrollment in student.enrollments
            if enrollment.class_
        ]
        return enrolled_classes


def get_students_for_class(class_id: str):
    with SessionLocal() as session:
        students = (
            session.query(Student)
            .join(Enrollment)
            .filter(Enrollment.class_id == class_id)
            .all()
        )
        students_data = []
        for student in students:
            enrollment = (
                session.query(Enrollment)
                .filter_by(student_id=student.user_id, class_id=class_id)
                .first()
            )
            class_info = session.query(Class).filter_by(class_id=class_id).first()
            if enrollment and class_info and class_info.possible_scores > 0:
                percentage_score = (enrollment.score / class_info.possible_scores) * 100
            else:
                percentage_score = None
            display_name = student.name
            students_data.append(
                {
                    "user_id": student.user_id,
                    "display_name": display_name,
                    "netid": student.user_id,
                    "percentage": (
                        f"{percentage_score:.2f}%"
                        if percentage_score is not None
                        else "N/A"
                    ),
                }
            )
        return students_data


def get_student_score_and_possible_for_class(user_id: str, class_id: str):
    """
    Retrieves the score of a specific student for a specific class and the possible score for that class.
    Args:
        student_id (str): The student's user ID.
        class_id (str): The class ID.
    Returns:
        tuple: A tuple containing the student's score and the possible score for the class.
               Returns (None, None) if the enrollment or class doesn't exist.
    """
    with SessionLocal() as session:
        enrollment = (
            session.query(Enrollment)
            .filter_by(user_id=user_id, class_id=class_id)
            .first()
        )
        class_info = session.query(Class).filter_by(class_id=class_id).first()

        if enrollment and class_info:
            return (enrollment.score, class_info.possible_scores)
        return (None, None)


def compute_percentage_score(score, possible_scores):
    if possible_scores > 0:
        return "{:.2f}%".format((score / possible_scores) * 100)
    else:
        return "N/A"


def get_professor_class(netid: str) -> str:
    """
    Retrieves the name of the class associated with a specific professor by their netID.
    Args:
        netid (str): The netID of the professor.
    Returns:
        str: The name of the class associated with the professor, or None if no class is found.
    """
    with SessionLocal() as session:
        professor_class = (
            session.query(Class.title)
            .join(Professor, Professor.user_id == Class.instructor_id)
            .filter(Professor.user_id == netid)
            .first()
        )
        if professor_class:
            return professor_class.title
        else:
            return None


def get_user_role(username):
    """
    Queries the database for the user's role based on their username.
    Args:
        username (str): The username of the user.
    Returns:
        str: The role of the user (e.g., 'student', 'professor') or None if not found.
    """
    with SessionLocal() as session:
        user = session.query(User).filter_by(user_id=username).first()
        if user:
            return user.role
        return None


def add_question_to_class(class_id: str, question_text: str, correct_answer: str):
    with SessionLocal() as session:
        new_question = Question(
            question_id=str(uuid.uuid4()),
            class_id=class_id,
            text=question_text,
            correct_answer=correct_answer,
        )
        session.add(new_question)
        try:
            session.commit()
            print(f"Question added to class {class_id}.")
            return new_question.question_id
        except SQLAlchemyError as e:
            print(f"Failed to add question to class {class_id}: {e}")
            session.rollback()
            return None


def get_professors_class_id(user_id):
    session = SessionLocal()
    try:
        professor_classes = (
            session.query(Class)
            .join(Professor, Class.instructor_id == Professor.user_id)
            .filter(Professor.user_id == user_id)
            .first()
        )
        if professor_classes:
            return professor_classes.class_id
        else:
            return None
    except Exception as e:
        print(f"Error fetching professor's class_id: {e}")
        return None
    finally:
        session.close()


def get_students_class_id(user_id):
    session = SessionLocal()
    try:
        student_class = (
            session.query(Class)
            .join(Enrollment, Class.class_id == Enrollment.class_id)
            .join(Student, Enrollment.student_id == Student.user_id)
            .filter(Student.user_id == user_id)
            .first()
        )
        if student_class:
            return student_class.class_id
        else:
            return None
    except Exception as e:
        print(f"Error fetching student's class_id: {e}")
        return None
    finally:
        session.close()
        

def get_active_class_and_session_ids(user_id, db_session: Session):
    """Fetch the class ID and active session ID for the specified user."""
    try:
        active_session = (
            db_session.query(ClassSession)
            .join(Class, Class.class_id == ClassSession.class_id)
            .join(User, Class.instructor_id == User.user_id)
            .filter(User.user_id == user_id, ClassSession.is_active == True)
            .first()
        )

        if active_session:
            return active_session.class_id, active_session.session_id
        else:
            return None, None
    except Exception as e:
        print(f"Error fetching active class and session IDs: {e}")
        return None, None



def get_questions_for_class(class_id: str):
    """
    Retrieves questions for a specific class ordered by their question_id to maintain consistency.

    Args:
        class_id (str): The unique identifier for the class.

    Returns:
        list: A list of dictionaries, each containing the question ID, text, and correct answer, ordered by creation.
    """
    with SessionLocal() as session:
        questions = session.query(Question).filter_by(class_id=class_id).order_by(Question.created_at).all()
        questions_data = [
            {
                "question_id": question.question_id,
                "text": question.text,
                "correct_answer": question.correct_answer
            }
            for question in questions
        ]
        return questions_data



def enroll_student(user_id, class_id):
    with SessionLocal() as session:
        new_enrollment = Enrollment(
            enrollment_id=str(uuid.uuid4()), student_id=user_id, class_id=class_id
        )
        session.add(new_enrollment)
        try:
            session.commit()
            print(f"Student {user_id} successfully enrolled in class {class_id}.")
            return True
        except Exception as e:
            print(f"Enrollment error: {e}")
            session.rollback()
            return False


def is_instructor_for_class(username, class_id):
    with SessionLocal() as db:
        instructor = (
            db.query(User)
            .filter(User.user_id == username, User.role == "professor")
            .first()
        )
        class_ = db.query(Class).filter_by(class_id=class_id).first()

        if instructor and class_ and class_.instructor_id == instructor.user_id:
            return True
        else:
            return False


def get_active_session_for_class(class_id):
    with SessionLocal() as db:
        active_session = (
            db.query(ClassSession).filter_by(class_id=class_id, is_active=True).first()
        )
        return active_session


def start_new_session(class_id):
    with SessionLocal() as db:
        try:
            new_session = ClassSession(
                session_id=str(uuid.uuid4()),
                class_id=class_id,
                start_time=datetime.now(),
                is_active=True,
            )
            db.add(new_session)
            db.commit()
            print(
                f"Session {new_session.session_id} for class {class_id} started at {new_session.start_time}"
            )
            return True, new_session.session_id
        except Exception as e:
            db.rollback()
            print(e)
            return False, None


def has_checked_in(username, session_id):
    with SessionLocal() as db:
        user = db.query(User).filter(User.user_id == username).first()
        if not user:
            return False
        attendance_record = (
            db.query(Attendance)
            .filter_by(student_id=user.user_id, session_id=session_id)
            .first()
        )

        return attendance_record is not None


def record_attendance_and_update(username, class_id, session_id):
    with SessionLocal() as db:
        student = db.query(Student).filter_by(user_id=username).first()
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=student.user_id, class_id=class_id)
            .first()
        )
        if not student or not enrollment:
            return False, "Student not enrolled or not found"
        if (
            db.query(Attendance)
            .filter_by(student_id=student.user_id, session_id=session_id)
            .first()
        ):
            return False, "Student already checked in"

        attendance = Attendance(
            attendance_id=str(uuid.uuid4()),
            session_id=session_id,
            student_id=student.user_id,
            timestamp=datetime.now(),
        )
        db.add(attendance)

        enrollment.sessions_attended += 1
        enrollment.score += 1

        try:
            db.commit()
            return True, "Check-in and update successful"
        except Exception as e:
            db.rollback()
            print(e)
            return False, "Failed to record attendance and update"


def is_student_enrolled_in_class(username, class_id):
    """
    Check if the student identified by the username is enrolled in the class specified by class_id.

    Args:
        username (str): The username (netID) of the student.
        class_id (str): The ID of the class.

    Returns:
        bool: True if the student is enrolled in the class, False otherwise.
    """
    with SessionLocal() as db:
        user = db.query(User).filter(User.user_id == username).first()
        if not user:
            return False
        enrollment = (
            db.query(Enrollment)
            .filter_by(student_id=user.user_id, class_id=class_id)
            .first()
        )
        return enrollment is not None


def update_question_status(question_id, class_id, is_active):
    session = SessionLocal()
    try:
        question = (
            session.query(Question)
            .filter_by(question_id=question_id, class_id=class_id)
            .first()
        )
        if question:
            question.is_active = is_active
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to update question status: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def update_question(question_id, new_text, new_answer, class_id):
    try:
        with SessionLocal() as session:
            question = (
                session.query(Question)
                .filter_by(question_id=question_id, class_id=class_id)
                .first()
            )
            if not question:
                print(f"No question found with ID {question_id} in class {class_id}")
                return False
            question.text = new_text
            question.correct_answer = new_answer
            session.commit()
            return True
    except Exception as e:
        print(f"Error updating question: {e}")
        return False


def get_active_questions_for_class(class_id):
    with SessionLocal() as session:
        active_questions = (
            session.query(Question).filter_by(class_id=class_id, is_active=True).all()
        )
        return active_questions


def is_question_active(question_id):
    with SessionLocal() as session:
        question = (
            session.query(Question)
            .filter_by(question_id=question_id, is_active=True)
            .first()
        )
        return question is not None


def submit_answer_for_question(question_id, student_id, answer_text):
    with SessionLocal() as session:
        existing_answer = (
            session.query(Answer)
            .filter_by(question_id=question_id, student_id=student_id)
            .first()
        )
        if existing_answer is not None:
            return "Answer already submitted"

        try:
            answer = Answer(
                answer_id=str(uuid.uuid4()),
                question_id=question_id,
                student_id=student_id,
                text=answer_text,
            )
            session.add(answer)
            session.commit()
            return "Answer submitted successfully"
        except Exception as e:
            session.rollback()
            return str(e)


def get_attendance_and_scores(class_id, student_id):
    with SessionLocal() as session:
        class_info = session.query(Class).filter_by(class_id=class_id).first()
        total_sessions_planned = class_info.total_sessions_planned if class_info else 0
        enrollment_info = (
            session.query(Enrollment)
            .filter_by(student_id=student_id, class_id=class_id)
            .first()
        )
        sessions_attended = enrollment_info.sessions_attended if enrollment_info else 0
        score = enrollment_info.score if enrollment_info else 0
        possible_scores = total_sessions_planned

        return {
            "attendance": sessions_attended,
            "totalSessions": total_sessions_planned,
            "score": score,
            "possibleScore": possible_scores,
        }


def check_question_not_active(
    session: Session, class_id: str, question_id: str
) -> bool:
    question = (
        session.query(Question)
        .filter_by(class_id=class_id, question_id=question_id)
        .first()
    )
    return question is not None and not question.is_active


def fetch_answers_generate_summary(session: Session, class_id: str, question_id: str) -> str:
    question = (
        session.query(Question)
        .filter_by(class_id=class_id, question_id=question_id)
        .first()
    )
    if not question:
        return "Question not found."

    answers = session.query(Answer).filter_by(question_id=question_id).all()
    student_answers = [answer.text for answer in answers]

    summarizer = TextSummarizer()
    summary = summarizer.summarize_student_answers(
        question.text, student_answers, question.correct_answer
    )
    notes = summarizer.learn_more(question.text, question.correct_answer)
    
    return summary, notes


def store_summary(session: Session, question_id: str, summary_text: str, explation: str):
    summary = session.query(Summary).filter_by(question_id=question_id).first()
    if not summary:
        summary = Summary(summary_id=str(uuid.uuid4()), question_id=question_id, text=summary_text, notes=explation)
        session.add(summary)
    else:
        summary.text = summary_text
    session.commit()
    

def get_feedback_data(session: Session, class_id: str, question_id: str) -> dict:
    question = session.query(Question).filter_by(class_id=class_id, question_id=question_id).first()
    summary = session.query(Summary).filter_by(question_id=question_id).first()

    if question and summary:
        feedback_data = {
            "question_content": question.text,
            "answers_summary": summary.text,
            "correct_answer": question.correct_answer,
            "notes": summary.notes
        }
        return feedback_data
    else:
        return None 
    

def fetch_user_answer(
    session: Session, question_id: str, user_id: str, user_role: str
) -> str:
    """
    Fetch a specific user's answer to a particular question, or return a message if the user is an instructor.

    Args:
    - session: The SQLAlchemy session for database operations.
    - question_id: The ID of the question.
    - user_id: The ID of the user whose answer is to be fetched.
    - user_role: The role of the user (e.g., "student" or "professor").

    Returns:
    - The text of the user's answer, a message indicating no answer for instructors, or None if no answer was found for a student.
    """
    if user_role == "professor":
        return "You are an instructor; you don't have a submitted answer."

    if user_role == "student":
        answer = (
            session.query(Answer)
            .filter_by(question_id=question_id, student_id=user_id)
            .first()
        )
        return answer.text if answer else "No answer submitted."
    return "Role not recognized."


def store_detailed_explanation(session, question_id, explanation_note):
    summary = session.query(Summary).filter_by(question_id=question_id).first()
    if summary:
        summary.notes = explanation_note 
    else:
        new_summary = Summary(summary_id=str(uuid.uuid4()), question_id=question_id, notes=explanation_note)
        session.add(new_summary)
    session.commit()
