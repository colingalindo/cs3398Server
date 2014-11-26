import unittest
from model.user import User
from model.appointment import Appointment
from model.base import Session, session_scope, Base, create_engine, create_schema
import jsonschema
from datetime import datetime

class AppointmentTest(unittest.TestCase):
	def setUp(self):
		create_engine('sqlite:///:memory:?check_same_thread=False', echo=True)
		create_schema()
		time = datetime.now()
		self.timeStr = time.strftime('%Y-%m-%d %H:%M:%S')
		
		session = Session()
		self.appointment = Appointment(1, 'Test Appointment 1', self.timeStr, self.timeStr)
		session.add(self.appointment)
		session.commit()

	def testConstructor(self):
		self.assertEqual(self.appointment.tutor_id, 1)
		self.assertEqual(self.appointment.name, 'Test Appointment 1')
		self.assertEqual(self.appointment.start_time, self.timeStr)
		self.assertEqual(self.appointment.end_time, self.timeStr)

	def testToJSON(self):
		data = self.appointment.toJSON()
		self.assertEqual(data['tutor_id'], 1)
		self.assertEqual(data['name'], 'Test Appointment 1')
		self.assertEqual(data['start_time'], self.timeStr)
		self.assertEqual(data['end_time'], self.timeStr)

	def testFromJson(self):
		appointment = Appointment.FromJSON({'tutor_id': 1, 'name': 'Test Appointment 2', 'start_time': self.timeStr, 'end_time': self.timeStr})
		self.assertEqual(appointment.tutor_id, 1)
		self.assertEqual(appointment.name, 'Test Appointment 2')
		self.assertEqual(appointment.start_time, self.timeStr)
		self.assertEqual(appointment.end_time, self.timeStr)

	def testFromJsonValidationError(self):
		self.assertRaises(jsonschema.exceptions.ValidationError, Appointment.FromJSON, ({'tutor_id': 1}))

if __name__ == "__main__":
	unittest.main()
