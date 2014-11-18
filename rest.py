import flask
import sqlalchemy
import json
import traceback, sys
from functools import wraps
from model.base import Session, session_scope
from controller.user import UserController, UserNotFound, AppointmentNotFound
from controller.appointment import AppointmentController
from model.user import User
from sqlalchemy.orm.exc import NoResultFound

api = flask.Blueprint('api', __name__)

class AuthenticationError(Exception):
	pass

def get_current_user(session):
	"""
	Helper for requires_auth. Returns the current user based on the request's Authorization headers.
	"""
	auth = flask.request.authorization
	username = auth.username
	password = auth.password

	user = session.query(User).filter(User.username == username)

	try:
		currentUser = user.one()
	except:
		raise AuthenticationError("Unknown User")

	if not currentUser.checkPassword(password):
		raise AuthenticationError("Bad Password")

	return currentUser

def rest_authentication_error(exc):
	"""
	Helper for requires_auth. Generates a 401 respose given an exception.
	"""
	res = flask.jsonify(status='error', errors=[exc.args[0]])
	res.status_code = 401 # unauthorized.
	res.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
	return res

def requires_auth(f):
	"""
	decorator for routes. Creates a session, queries for the current user using the
	current auth, and either returns a 401 error if the authorization info is wrong,
	or returns the result of the wrapped function.
	"""
	@wraps(f)
	def decorated(*args, **kwargs):
		with session_scope() as session:
			try:
				currentUser = get_current_user(session)
			except AuthenticationError as exc:
				# TODO: use logger for this exception...
				traceback.print_exc(file=sys.stdout)
				return rest_authentication_error(exc)

			return f(session, currentUser, *args, **kwargs)
	return decorated

@api.route('/', methods=['GET'])
def hello_api():
    return "HELLO FROM THE API!"


@api.route('/server-info', methods=['GET'])
def get_server_info():
    return json.dumps({
        'sqlalchemy_version': sqlalchemy.__version__
    })


@api.route('/users', methods=['GET'])
@requires_auth
def get_users(session, currentUser):
	controller = UserController(session)
	users = controller.get_users()
	return flask.jsonify({'users':users})

@api.route('/users', methods=['POST'])
@requires_auth
def post_user(session, currentUser):
	controller = UserController(session)
	data = flask.request.get_json()
	result = controller.post_user(data)
	return flask.jsonify(result)

@api.route('/users/<user_id>', methods=['PUT'])
@requires_auth
def put_user(session, currentUser, user_id):
	controller = UserController(session)
	data = flask.request.get_json()
	try:
		res = flask.jsonify(controller.put_user(user_id, data))
	except NoResultFound:
		res = flask.jsonify(status='error', errors=['could not find user'])
		res.status_code = 404
	return res

@api.route('/users/<user_id>', methods=['GET'])
@requires_auth
def get_user(session, currentUser, user_id):
	controller = UserController(session)
	try:
		res = flask.jsonify(controller.get_user(user_id))
	except NoResultFound:
		res = flask.jsonify(status='error', errors=['could not find user'])
		res.status_code = 404
	return res

@api.route('/users/<user_id>/appointments', methods=['POST'])
@requires_auth
def add_appointments_to_user(session, currentUser, user_id):
	controller = UserController(session)
	data = flask.request.get_json()
	try:
		res = flask.jsonify(controller.add_appointments_to_user(user_id, data))
	except UserNotFound:
		res = flask.jsonify(status='error', errors=['could not find user'])
		res.status_code = 404
	except AppointmentNotFound:
		res = flask.jsonify(status='error', errors=['could not find appointment'])
		res.status_code = 404
	return res

@api.route('/users/<user_id>/appointments', methods=['GET'])
@requires_auth
def get_appointments_from_user(session, currentUser, user_id):
	controller = UserController(session)
	try:
		res = flask.jsonify({'appointments':controller.get_appointments_from_user(user_id)})
	except UserNotFound:
		res = flask.jsonify(status='error', errors=['could not find user'])
		res.status_code = 404
	return res

@api.route('/appointments', methods=['GET'])
@requires_auth
def get_appointments(session, currentUser):
	controller = AppointmentController(session)
	appointments = controller.get_appointments()
	return flask.jsonify({'appointments':appointments})

@api.route('/appointments', methods=['POST'])
@requires_auth
def post_appointments(session, currentUser):
	controller = AppointmentController(session)
	data = flask.request.get_json()
	result = controller.post_appointment(data)
	return flask.jsonify(result)
