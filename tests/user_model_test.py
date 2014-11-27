import unittest
from model.user import User
from model.appointment import Appointment
from model.base import Session, session_scope, Base, create_engine, create_schema
import jsonschema

class UserTest(unittest.TestCase):
	def setUp(self):
		create_engine('sqlite:///:memory:?check_same_thread=False', echo=True)
		create_schema()

		session = Session()
		self.user = User("username", "password", "fullname")
		session.add(self.user)
		session.commit()

	def testConstructor(self):
		self.assertEqual(self.user.username, "username")
		self.assertTrue(self.user.checkPassword("password"))
		self.assertEqual(self.user.fullname, "fullname")
		self.assertEqual(self.user.status, User.STATUS_ACTIVE)
		self.assertEqual(self.user.role, User.ROLE_STUDENT)

	def testArchive(self):
		self.user.archive()
		self.assertEqual(self.user.status, User.STATUS_ARCHIVED)

	def testUnarchive(self):
		self.user.archive()
		self.user.unarchive()
		self.assertEqual(self.user.status, User.STATUS_ACTIVE)

	def testToJSON(self):
		data = self.user.toJSON()
		self.assertEqual(data['username'], 'username')
		self.assertEqual(data['fullname'], 'fullname')
		self.assertEqual(data['user_id'], self.user.id)
		self.assertEqual(data['status'], 'active')
		self.assertEqual(data['role'], 'student')

	def testSetPassword(self):
		self.user.setPassword("foobar")
		self.assertTrue(self.user.checkPassword("foobar"))

	def testFromJson(self):
		user = User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1', 'email': 'name.1@email.com', 'work_number': '5554443333', 'mobile_number': '5553334444'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.email, 'name.1@email.com')
		self.assertEqual(user.work_number, '5554443333')
		self.assertEqual(user.mobile_number, '5553334444')
		self.assertEqual(user.status, User.STATUS_ACTIVE)
		self.assertEqual(user.role, User.ROLE_STUDENT)
		self.assertTrue(user.checkPassword('blech'))

	def testStatusFromJson(self):
		user = User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1', 'status': 'archived'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.status, User.STATUS_ARCHIVED)
		self.assertTrue(user.checkPassword('blech'))

	def testRoleFromJson(self):
		user = User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1', 'status': 'archived', 'role': 'tutor'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.status, User.STATUS_ARCHIVED)
		self.assertEqual(user.role, User.ROLE_TUTOR)
		self.assertTrue(user.checkPassword('blech'))

	def testFromJsonValidationError(self):
		self.assertRaises(jsonschema.exceptions.ValidationError, User.FromJSON, ({'username': 'blah'}))

if __name__ == "__main__":
	unittest.main()
