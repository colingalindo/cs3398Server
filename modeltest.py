import unittest
import model
import jsonschema

class UserTest(unittest.TestCase):
	def setUp(self):
		model.create_engine('sqlite:///:memory:?check_same_thread=False', echo=True)
		model.create_schema()

		session = model.Session()
		self.user = model.User("username", "password")
		session.add(self.user)
		session.commit()

	def testConstructor(self):
		self.assertEqual(self.user.username, "username")
		self.assertTrue(self.user.checkPassword("password"))
		self.assertEqual(self.user.status, model.User.STATUS_ACTIVE)

	def testArchive(self):
		self.user.archive()
		self.assertEqual(self.user.status, model.User.STATUS_ARCHIVED)

	def testUnarchive(self):
		self.user.archive()
		self.user.unarchive()
		self.assertEqual(self.user.status, model.User.STATUS_ACTIVE)

	def testGetJSON(self):
		data = self.user.getJSON()
		self.assertEqual(data['username'], 'username')
		self.assertEqual(data['userID'], self.user.userID)
		self.assertEqual(data['status'], self.user.status)

	def testSetPassword(self):
		self.user.setPassword("foobar")
		self.assertTrue(self.user.checkPassword("foobar"))

	def testFromJson(self):
		user = model.User.FromJSON({'username': 'blah', 'password': 'blech'})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.status, model.User.STATUS_ACTIVE)
		self.assertTrue(user.checkPassword('blech'))

	def testStatusFromJson(self):
		user = model.User.FromJSON({'username': 'blah', 'password': 'blech', 'status': model.User.STATUS_ARCHIVED})
		self.assertEqual(user.username, 'blah')
		self.assertEqual(user.status, model.User.STATUS_ARCHIVED)
		self.assertTrue(user.checkPassword('blech'))

	def testFromJsonValidationError(self):
		self.assertRaises(jsonschema.exceptions.ValidationError, model.User.FromJSON, ({'username': 'blah'}))

	def testPatchMyAccount(self):
		data = {
			'ops': [
				{
					'op': 'setPassword',
					'password': 'foobar'
				}
			]
		}

		self.user.patchMyAccount(data)
		self.assertTrue(self.user.checkPassword('foobar'))

	def testPatchMyAccountException(self):
		data = {
			'ops': [
				{
					'badop': 'setPassword',
					'password': 'foobar'
				}
			]
		}

		self.assertRaises(jsonschema.exceptions.ValidationError, self.user.patchMyAccount, (data))



if __name__ == "__main__":
	unittest.main()