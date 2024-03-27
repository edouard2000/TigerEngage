#!/usr/bin/env python

#-----------------------------------------------------------------------
# database.py
# Author: Jourdain Babisa
#-----------------------------------------------------------------------

import os
import sqlalchemy
import sqlalchemy.orm
import user as usermodpwd

#-----------------------------------------------------------------------

_DATABASE_URL = os.environ['DATABASE_URL']
_DATABASE_URL = _DATABASE_URL.replace('postgres://', 'postgresql://')

#-----------------------------------------------------------------------

# Create an engine to connect to database
_engine = sqlalchemy.create_engine(_DATABASE_URL)

Base = sqlalchemy.orm.declarative_base()

class User (Base):
    __tablename__ = 'users'
    user_id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String)
    role = sqlalchemy.Column(sqlalchemy.Enum('student', 'professor', name='role'))
    name = sqlalchemy.Column(sqlalchemy.String)

class Class(Base):
    __tablename__ = 'classes'
    class_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    instructor_id = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.user_id'))
    instructor = sqlalchemy.orm.relationship('User', back_populates='classes')

# Add a classes relationship to the User class
User.classes = sqlalchemy.orm.relationship('Class', back_populates='instructor')

class Session(Base):
    __tablename__ = 'sessions'

    session_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    class_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('classes.class_id'))
    start_time = sqlalchemy.Column(sqlalchemy.DateTime)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime)
    
    # Define the relationship with the Class table
    class_obj = sqlalchemy.orm.relationship('Class', back_populates='sessions')

# Add a sessions relationship to the Class class
Class.sessions = sqlalchemy.orm.relationship('Session', back_populates='class_obj')

# Create the tables in the database
Base.metadata.create_all(_engine)

#-----------------------------------------------------------------------

def get_users(role):
    users = []
    with sqlalchemy.orm.Session(_engine) as session:
        query = session.query(User).filter(User.role == role)
        table = query.all()
        for row in table:
            user = usermod.User(row.user_id, row.email, row.password_hash, row.role, row.name)
            users.append(user)
    return users

def get_classes(instructor_id):
    classes = []
    with sqlalchemy.orm.Session(_engine) as session:
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

def get_sessions(class_id):
    sessions = []
    with sqlalchemy.orm.Session(_engine) as session:
        query = session.query(Session).filter(Session.class_id == class_id)
        table = query.all()
        for row in table:
            session_info = {
                'session_id': row.session_id,
                'class_id': row.class_id,
                'start_time': row.start_time,
                'end_time': row.end_time
            }
            sessions.append(session_info)
    return sessions

#-----------------------------------------------------------------------

# For testing:

def _test():
    user1 = User(user_id='1', email='johndoe45@princeton.edu', password_hash='password123', role='student', name='John Doe')
    user2 = User(user_id='5', email='janedoe@princeton.edu', password_hash='password321', role='student', name='Jane Doe')
    user3 = User(user_id='6', email='maryjane@princeton.edu', password_hash='spiderman', role='student', name='Mary Jane')
    Session = sqlalchemy.orm.sessionmaker(bind=_engine)
    session = Session()
    # session.add(user1)
    # session.add(user2)
    # session.add(user3)
    session.query(User).delete()
    session.commit()
    session.close()
    print("All rows deleted successfully.")
    users = get_users('student')
    for user in users:
        print(user.get_user_id())
        print(user.get_email())
        print(user.get_password_hash())
        print(user.get_role())
        print(user.get_name())
        print()

if __name__ == '__main__':
    _test()
