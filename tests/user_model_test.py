import unittest
from model.base import Base
import model.user
import jsonschema

class UserTest(unittest.TestCase):
	def setUp(self):
		model.base.create_engine('sqlite:///:memory:?check_same_thread=False', echo=True)
		model.base.create_schema()

		session = model.base.Session()
		self.user = model.user.User("username", "password", "fullname")
		session.add(self.user)
		session.commit()

	def testConstructor(self):
		self.assertEqual(self.user.username, "username")
		self.assertTrue(self.user.checkPassword("password"))
		self.assertEqual(self.user.fullname, "fullname")
		self.assertEqual(self.user.status, model.user.User.STATUS_ACTIVE)
		self.assertEqual(self.user.role, model.user.User.ROLE_STUDENT)

	def testArchive(self):
		self.user.archive()
		self.assertEqual(self.user.status, model.user.User.STATUS_ARCHIVED)

	def testUnarchive(self):
		self.user.archive()
		self.user.unarchive()
		self.assertEqual(self.user.status, model.user.User.STATUS_ACTIVE)

	def testToJSON(self):
		data = self.user.toJSON()
		self.assertEqual(data['username'], 'username')
		self.assertEqual(data['fullname'], 'fullname')
		self.assertEqual(data['userID'], self.user.id)
		self.assertEqual(data['status'], 'active')
		self.assertEqual(data['role'], 'student')

	def testSetPassword(self):
		self.user.setPassword("foobar")
		self.assertTrue(self.user.checkPassword("foobar"))

	def testFromJson(self):
		user = model.user.User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.status, model.user.User.STATUS_ACTIVE)
		self.assertEqual(user.role, model.user.User.ROLE_STUDENT)
		self.assertTrue(user.checkPassword('blech'))

	def testStatusFromJson(self):
		user = model.user.User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1', 'status': 'archived'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.status, model.user.User.STATUS_ARCHIVED)
		self.assertTrue(user.checkPassword('blech'))

	def testRoleFromJson(self):
		user = model.user.User.FromJSON({'username': 'blah', 'password': 'blech', 'fullname': 'name 1', 'status': 'archived', 'role': 'tutor'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.fullname, 'name 1')
		self.assertEqual(user.status, model.user.User.STATUS_ARCHIVED)
		self.assertEqual(user.role, model.user.User.ROLE_TUTOR)
		self.assertTrue(user.checkPassword('blech'))

	def testFromJsonValidationError(self):
		self.assertRaises(jsonschema.exceptions.ValidationError, model.user.User.FromJSON, ({'username': 'blah'}))

if __name__ == "__main__":
	unittest.main()
