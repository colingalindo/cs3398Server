"""
This requires a server to run at http://localhost:5000/. It requires a 
with the username/password from AUTH_PARAMS and no others.
"""

import requests
import unittest
import jsonschema
import json


USER_JSON = {
	'type': 'object',
	'properties': {
		'userID': {
			'type': 'integer',
		},
		'username': {
			'type': 'string'
		},
		'status': {
			'enum': ['active', 'archived']
		}
	},
	'required': ['userID', 'username', 'status']
}

GET_USERS_RESPONSE_SCHEMA = {
	'title': 'GET_USERS_RESPONSE_SCHEMA',
	'type': 'object',
	'properties': {
		'users': {
			'type': 'array',
			'items': USER_JSON
		}
	},
	'required': ['users']
}

POST_USERS_RESPONSE_SCHEMA = {
	'title': 'POST_USERS_RESPONSE_SCHEMA',
	'type': 'object',
	'oneOf': [
		{
			'type': 'object',
			'properties': {
				'status': {
					'enum': ['success']
				},
				'user': USER_JSON
			},
			'required': ['user', 'status']
		},
		{
			'type': 'object',
			'properties': {
				'status': {
					'enum': ['failure']
				}
			},
			'required': ['status']
		}
	],
	'required': ['status']
}

# This needs to be run against an existing server at the following url base URL
SERVER_BASE_URL = "http://localhost:5000/"
API_BASE_URL = SERVER_BASE_URL + "api/v1.0/"
AUTH_PARAMS = ('neb', 'foobar')

class RestUsersTest(unittest.TestCase):
	def testGetUsers(self):
		url = API_BASE_URL + "users"
		response = requests.get(url, auth = AUTH_PARAMS)
		data = response.json()
		jsonschema.validate(data, GET_USERS_RESPONSE_SCHEMA)

	def testPostUsers(self):
		"""
		This is a bit fragile; we need a way of resetting the database...
		"""
		url = API_BASE_URL + "users"
		user_json = {
			'username': 'bob',
			'password': 'baz'
		}

		headers = {'content-type': 'application/json'}
		response = requests.post(url, auth=AUTH_PARAMS, headers=headers, data=json.dumps(user_json))
		data = response.json()
		user = data['user']
		self.assertEqual(response.status_code, 200)
		self.assertEqual(user['username'], 'bob')
		self.assertEqual(user['status'], 'active')
		self.assertEqual(data['status'], 'success')

		print("RESPONSE:",response.text)
		data = response.json()
		jsonschema.validate(data, POST_USERS_RESPONSE_SCHEMA)

		# delete bob.
		params={'debug_delete':True}
		response = requests.delete(url + "/" + str(data['user']['userID']), auth=AUTH_PARAMS, headers=headers, params=params)
		self.assertEqual(response.status_code, 200)

	def testPutUser(self):
		pass

	def testPatchUser(self):
		pass


if __name__ == "__main__":
	unittest.main()