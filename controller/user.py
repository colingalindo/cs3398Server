from model.user import User
from model.base import Session, session_scope
from sqlalchemy.orm.exc import NoResultFound
import flask
from model.appointment import Appointment

class UserNotFound(Exception):
    pass

class AppointmentNotFound(Exception):
    pass

class UserController(object):

    def __init__(self, session):
        super(UserController, self).__init__()
        self.session = session

    def get_users(self):
        users = self.session.query(User).all()
        return [u.toJSON() for u in users]

    def post_user(self, data):
        user = User.FromJSON(data)
        self.session.add(user)
        self.session.flush()
        return user.toJSON()

    def put_user(self, user_id, data):
        users = self.session.query(User).filter(User.id == user_id)
        user = users.one()
        if 'username' in data:
            user.username = data['username']
        if 'password' in data:
            user.password = User.getDigest(data['password'])
        if 'fullname' in data:
            user.fullname = data['fullname']
        self.session.add(user)
        return user.toJSON()

    def get_user(self, user_id):
        users = self.session.query(User).filter(User.id == user_id)
        user = users.one()
        return user.toJSON()

    def add_appointments_to_user(self, user_id, data):
        users = self.session.query(User).filter(User.id == user_id)
        try:
            user = users.one()
        except NoResultFound as userNotFound:
            raise UserNotFound()
        for appointment_id in data['appointment_ids']:
            appointments = self.session.query(Appointment).filter(Appointment.id == appointment_id)
            try:
                appointment = appointments.one()
            except NoResultFound as appointmentNotFound:
                raise AppointmentNotFound()
            user.appointments.append(appointment)
        self.session.add(user)
        return user.toJSON()

    def get_appointments_from_user(self, user_id):
        users = self.session.query(User).filter(User.id == user_id)
        try:
            user = users.one()
        except NoResultFound as userNotFound:
            raise UserNotFound()
        return [a.id for a in user.appointments]
