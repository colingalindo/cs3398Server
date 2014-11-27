from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base
import jsonschema
import werkzeug

user2appointment_table = Table('user2appointment', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('appointment_id', Integer, ForeignKey('appointments.id'))
)

class User(Base):
    __tablename__ = 'users'

    STATUS_ACTIVE = 0
    STATUS_ARCHIVED = 1

    ROLE_STUDENT = 0
    ROLE_TUTOR = 1

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    fullname = Column(String(64))
    password = Column(String(256))
    email = Column(String(64))
    work_number = Column(String(10))
    mobile_number = Column(String(10))
    role = Column(Integer, default=ROLE_STUDENT, nullable=False)
    status = Column(Integer, default=STATUS_ACTIVE)

    appointments = relationship("Appointment", secondary=user2appointment_table)

    # used to produce more human-readable json responses for role property
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

    def __init__(self, username, password, fullname, email=None, work_number=None, mobile_number=None, role = ROLE_STUDENT, status = STATUS_ACTIVE, *args, **kwds):
        super(User, self).__init__(username=username, password=User.getDigest(password), fullname=fullname, email=email, work_number=work_number, mobile_number=mobile_number, role=role, status=status, *args, **kwds)

    def __repr__(self):
       return "<User(username='%s', password='%s', fullname='%s', email='%s', work_number='%s', mobile_number='%s', role=%s, status=%s)>" % (self.username, self.password, self.fullname, self.email, self.work_number, self.mobile_number, self.role, self.status)

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

    def toJSON(self):
        """
        Returns a json-serializable object for the rest interface.
        """
        return {
            'user_id': self.id,
            'username': self.username,
            'fullname': self.fullname,
            'email': self.email,
            'work_number': self.work_number,
            'mobile_number': self.mobile_number,
            'role': User.ROLE_MAP[self.role],
            'status': User.STATUS_MAP[self.status],
            'appointments': [a.toJSON() for a in self.appointments]
        }

    @classmethod
    def FromJSON(cls, jsonData):
        print("JSON:",jsonData)

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
                'fullname': {
                    'type': 'string'
                },
                'email': {
                    'type': 'string'
                },
                'work_number': {
                    'type': 'string'
                },
                'mobile_number': {
                    'type': 'string'
                },
                'role': {
                    'enum': ['student', 'tutor']
                },
                'status': {
                    'enum': ['archived', 'active']
                }
            },
            'required': ['username', 'password', 'fullname']
        }
        # this will raise an error if the schema does not validate
        jsonschema.validate(jsonData, USER_POST_SCHEMA)
        jsonData['status'] = User.STATUS_REVERSE_MAP[jsonData.pop('status', 'active')]
        jsonData['role'] = User.ROLE_REVERSE_MAP[jsonData.pop('role', 'student')]
        return cls(**jsonData)
