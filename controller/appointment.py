from model.appointment import Appointment
from model.base import Session, session_scope
from sqlalchemy.orm.exc import NoResultFound
import flask

class AppointmentController(object):

    def __init__(self, session):
        super(AppointmentController, self).__init__()
        self.session = session

    def get_appointments(self):
        appointments = self.session.query(Appointment).all()
        return [a.toJSON() for a in appointments]

    def post_appointment(self, data):
        appointment = Appointment.FromJSON(data)
        self.session.add(appointment)
        self.session.flush()
        return appointment.toJSON()

    def put_appointment(self, appointment_id, data):
        appointments = self.session.query(Appointment).filter(Appointment.id == appointment_id)
        appointment = appointments.one()
        if 'tutorID' in data:
            appointment.tutorID = data['tutorID']
        self.session.add(apointment)
        return appointment.toJSON()

    def get_appointment(self, appointment_id):
        appointments = self.session.query(Appointment).filter(Appointment.id == appointment_id)
        appointment = appointments.one()
        return appointment.toJSON()
