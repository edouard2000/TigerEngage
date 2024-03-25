#!/usr/bin/env python

#-----------------------------------------------------------------------
# book.py
# Author: Bob Dondero
#-----------------------------------------------------------------------

class User:

    def __init__(self, user_id, email, password_hash, role, name):
        self._user_id = user_id
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._name = name

    def get_user_id(self):
        return self._user_id

    def get_email(self):
        return self._email

    def get_password_hash(self):
        return self._password_hash
    
    def get_role(self):
        return self._role
    
    def get_name(self):
        return self._name

    def to_tuple(self):
        return (self._user_id, self._email, self._password_hash, self._role, self.name)

#-----------------------------------------------------------------------

def _test():
    user = User('1', 'johndoe1@princeton.edu', 'password123', 'student', 'John Doe')
    print(user.get_user_id())
    print(user.get_email())
    print(user.get_password_hash())
    print(user.get_role())
    print(user.get_name())
    print(user.to_tuple())

if __name__ == '__main__':
    _test()
