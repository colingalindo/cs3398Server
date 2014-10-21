"""
The model module.

"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Sequence
from sqlalchemy.orm.exc import NoResultFound
import werkzeug
import jsonschema

import base64
import datetime
import os
from contextlib import contextmanager
import json

Base = declarative_base()
Session = sessionmaker()
engine = None


def set_engine(_engine):
    """
    Sets the database engine used by the model. For testing this should be an in-memory SQLite database, for production
    it should be something like MySQL.
    """
    global engine
    engine = _engine
    Base.metadata.bind = engine
    Session.configure(bind=engine)


def create_engine(uri, echo=True):
    """
    Sets the database engine from a database connection string.
    """
    set_engine(sqlalchemy.create_engine(uri, echo=echo))


def teardown():
    """
    Unsets the database engine.
    """
    Session.remove()


@contextmanager
def session_scope():
    """
    Provide a transactional scope around a series of operations.

    This will automatically rollback the session on an exception, then re-raise the exception.

    On success it commits.

    On success or failure, it closes the session.
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class User(Base):
    __tablename__ = "User"

    STATUS_ACTIVE = 0
    STATUS_ARCHIVED = 1

    ROLE_STUDENT = 0
    ROLE_TUTOR = 1

    userID = Column(Integer, Sequence('User_id_seq'), primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) # actually the salted hash of the password
    role = Column(Integer, default=ROLE_STUDENT, nullable=False)
    status = Column(Integer, default=STATUS_ACTIVE)

    ROLE_MAP = {
        ROLE_STUDENT: 'student',
        ROLE_TUTOR: 'tutor'
    }

    ROLE_REVERSE_MAP = {
        v:k for k,v in ROLE_MAP.items()
    }

    # used to produce more human-readable json responses for status property.
    STATUS_MAP = {
        STATUS_ACTIVE: 'active',
        STATUS_ARCHIVED: 'archived'
    }

    STATUS_REVERSE_MAP = {
        v:k for k,v in STATUS_MAP.items()
    }

    def __init__(self, username, password, role = ROLE_STUDENT, status = STATUS_ACTIVE, *args, **kwds):
        print("CONSTRUCTING USER:", username, password, role, status, args, kwds)
        super(User, self).__init__(username=username, password=User.getDigest(password), role=role, status=status, *args, **kwds)

    def archive(self):
        """
        Sets a user's status to archived.
        """
        self.status = User.STATUS_ARCHIVED

    def unarchive(self):
        """
        Sets a user's status to active.
        """
        self.status = User.STATUS_ACTIVE

    def __repr__(self):
        """
        Generates a string representation of the user for debugging purposes.
        """
        return "User(userID=%s, username=%s, password=%s, role=%s, status=%s)" % (self.userID, self.username, self.password, self.role, self.status)

    def getJSON(self):
        """
        Returns a json-serializable object for the rest interface.
        """
        print("GETJSON CALLED:", self)
        return {
            'userID': self.userID,
            'username': self.username,
            'role': User.ROLE_MAP[self.role],
            'status': User.STATUS_MAP[self.status]
        }

    def getMyAccountJSON(self):
        """
        Returns a json-serializable object for the rest interface.
        """
        print("GETMYACCOUNTJSON CALLED:", self)
        return {
            'userID': self.userID,
            'username': self.username,
            'role': User.ROLE_MAP[self.role],
            'status': User.STATUS_MAP[self.status]
        }

    @staticmethod
    def getDigest(password):
        """
        Generate a digest for the salted hash of a password.
        """
        return werkzeug.generate_password_hash(password)

    def checkPassword(self, password):
        """
        Returns true if the password is correct, false otherwise.
        """
        return werkzeug.check_password_hash(self.password, password)

    def setPassword(self, password):
        """
        Sets User.password to a salted hash.
        """
        self.password = User.getDigest(password)

    def patchMyAccount(self, patch_json):
        """
        handles JSON from a PATCH request to "/MyAccount".
        """
        print("PATCHMYACCOUNT CALLED:", self)
        MYACCOUNT_PATCH_SCHEMA = {
            'title': '/MyAccount PATCH Schema',
            'type': 'object',
            'definitions': {
                'setPassword': {
                    'type': 'object',
                    'required': ['op', 'password'],
                    'properties': {
                        'op': {
                            'enum': ['setPassword']
                        },
                        'password': {
                            'type': 'string'
                        }
                    }
                }
            },
            'required': ['ops'],
            'properties': {
                'ops': {
                    'type': 'array',
                    'items': {
                        'oneOf': [
                            {'$ref': '#/definitions/setPassword'}
                        ]
                    }
                }
            }
        }

        jsonschema.validate(patch_json, MYACCOUNT_PATCH_SCHEMA)

        ops = patch_json['ops']
        for op in ops:
            if op['op'] == 'setPassword':
                self.setPassword(op['password'])
            else:
                raise NotImplementedError("unknown op:", op['op'])


    @classmethod
    def FromJSON(cls, jsonData):
        """
        Creates a user from a partial (the userID is omitted) json representation of the user.

        {
            'username': 'string',
            'password': 'string'
        }
        """
        print(jsonData)

        # validate the schema
        USER_POST_SCHEMA = {
            'title': 'User POST Schema',
            'type': 'object',
            'properties': {
                'username': {
                    'type': 'string'
                },
                'password': {
                    'type': 'string'
                },
                'role': {
                    'enum': ['student', 'tutor']
                },
                'status': {
                    'enum': ['archived', 'active']
                }
            },
            'required': ['username', 'password']
        }

        # this will raise an error if the schema does not validate
        jsonschema.validate(jsonData, USER_POST_SCHEMA)
        print(jsonData)
        jsonData['status'] = User.STATUS_REVERSE_MAP[jsonData.pop('status', 'active')]
        jsonData['role'] = User.ROLE_REVERSE_MAP[jsonData.pop('role', 'student')]
        return User(**jsonData)

class LogEntry(Base):
    __tablename__ = "LogEntry"

    logEntryID = Column(Integer, Sequence('LogEntry_id_seq'), primary_key=True)
    dateTime = Column(DateTime)
    jsonData = Column(String)
    type = Column(String)

    def getJSON(self):
        return {}

    def __repr__(self):
        return "LogEntry(logEntryID=%s, type=%s, jsonData=%s)" % (self.logEntryID, repr(self.jsonData), repr(self.message))


def create_schema():
    Base.metadata.create_all(engine)


def create_data():
    with session_scope() as session:
        if session.query(User).filter(User.username == "neb").count() != 0:
            return

        username = "neb"
        password = "foobar"
        role = User.ROLE_TUTOR
        user = User(username, password, role)

        assert(user.checkPassword("foobar"))

        session.add(user)
