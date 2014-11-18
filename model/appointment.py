from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from .base import Base
import jsonschema
import werkzeug

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    tutor_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    start_time = Column(String)
    end_time = Column(String)

    def __init__(self, tutor_id, name, start_time, end_time, *args, **kwds):
        super(Appointment, self).__init__(tutor_id=tutor_id, name=name, start_time=start_time, end_time=end_time, *args, **kwds)

    def __repr__(self):
       return "<Appointment(tutorID='%s', name='%s', start_time='%s', end_time='%s')>" % (self.tutor_id, self.name, self.start_time, self.end_time)

    def toJSON(self):
        """
        Returns a json-serializable object for the rest interface.
        """
        return {
            'appointmentID': self.id,
            'tutorID': self.tutor_id,
            'name': self.name,
            'start_time': self.start_time,
            'end_time': self.end_time
        }

    @classmethod
    def FromJSON(cls, jsonData):
        print("JSON:",jsonData)

        # validate the schema
        APPOINTMENT_POST_SCHEMA = {
            'title': 'Appointment POST Schema',
            'type': 'object',
            'properties': {
                'tutor_id': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'string'
                },
                'start_time': {
                    'type': 'string'
                },
                'end_time': {
                    'type': 'string'
                }
            },
            'required': ['tutor_id', 'name', 'start_time', 'end_time']
        }
        # this will raise an error if the schema does not validate
        jsonschema.validate(jsonData, APPOINTMENT_POST_SCHEMA)
        return cls(**jsonData)
