import flask
import json
import model
import hashlib
from model import Session, User, session_scope
from sqlalchemy.orm.exc import NoResultFound
from functools import wraps
import traceback
import sys
import logging

api = flask.Blueprint('rest_api', __name__)

debugLog = logging.getLogger(__name__)
debugLog.setLevel(logging.DEBUG)

fhandler = logging.FileHandler(filename='debug.log')
fhandler.setLevel(logging.DEBUG)

debugLog.addHandler(fhandler)

# debugLog.basicConfig(filename='debug.log', level=logging.DEBUG)

class AuthenticationError(Exception):
    pass


def get_current_user(session):
    """
    Helper for requires_auth. Returns the current user based on the request's Authorization headers.
    """
    auth = flask.request.authorization
    username = auth.username
    password = auth.password

    print("username:",username,"password:",password)

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


@api.route('/myaccount', methods=['GET'])
@requires_auth
def get_myaccount(session, currentUser):
    """
    Returns a json representation of the current user.

    {
        "userID": 1123,
        "username": "foo"
    }
    """
    return flask.jsonify(**currentUser.getMyAccountJSON())


@api.route('/myaccount', methods=['PATCH'])
@requires_auth
def patch_myaccount(session, currentUser):
    """
    Edit certain aspects of the current user, including:

    set the current user's password. (TODO: test this).

    To set the current user's password to "new_password", send the following json:
    {
        'ops': [
            {
                'op': 'setPassword',
                'password': 'newPassword'
            }
        ]
    }
    """
    data = flask.request.get_json()
    currentUser.patchMyAccount(data)
    session.add(currentUser)
    return flask.jsonify(**currentUser.getMyAccountJSON())


@api.route('/users', methods=['GET'])
@requires_auth
def get_users(session, currentUser):
    """
    GET a user from a session.

    TODO: get permissions based on currentUser.
    TODO: pagination
    TODO: filters
    """
    users = session.query(User).filter(User.status != User.STATUS_ARCHIVED)
    return flask.jsonify(users=[u.getJSON() for u in users])


@api.route('/users', methods=['POST'])
@requires_auth
def post_users(session, currentUser):
    """
    POST a user with a session.

    TODO: Get permissions based on currentUser.
    """
    print (flask.request.headers)

    data = flask.request.get_json()
    debugLog.info("data: %s", data)
    user = User.FromJSON(data)
    session.add(user)
    session.flush()
    debugLog.info("user: %s", data)
    return flask.jsonify(status='success', user=user.getJSON())


@api.route('/users/<user_id>', methods=['DELETE'])
@requires_auth
def delete_user(session, currentUser, user_id):
    """
    GET a user from a session.

    TODO: get permissions based on currentUser.
    TODO: set the user's status to STATUS_ARCHIVED instead of deleting.
    """
    users = session.query(User).filter(User.userID == user_id)

    try:
        user = users.one()
    except NoResultFound:
        res = flask.jsonify(errors=['could not find user'])
        res.status_code = 404
        return res

    # TODO: enable/disable this during testing.
    print(flask.request.args)
    if flask.request.args.get('debug_delete', False):
        print("DEBUG DELETE")
        session.delete(user)
    else:
        user.archive()
        session.add(user)

    return flask.jsonify(status='success')


@api.route('/users/<user_id>', methods=['GET'])
@requires_auth
def get_user(session, currentUser, user_id):
    users = session.query(User).filter(User.userID == user_id)

    try:
        user = users.one()
    except NoResultFound:
        res = flask.jsonify(status='error', errors=['could not find user'])
        res.status_code = 404
        return res

    return flask.jsonify(user=users[0].getJSON())


@api.route('/users/<user_id>', methods=['PUT'])
@requires_auth
def put_user(session, currentUser, user_id):
    data = flask.request.get_json()

    users = session.query(User).filter(User.userID == user_id)

    try:
        user = users.one()
    except NoResultFound:
        res = flask.jsonify(status='error', errors=['could not find user'])
        res.status_code = 404
        return res

    if 'username' in data:
        user.username = data['username']

    if 'password' in data:
        user.password = data['password']

    session.add(user)

    return flask.jsonify(user=user.getJSON())


@api.route('/users/archived', methods=['GET'])
@requires_auth
def get_archived_users(session):
    users = session.query(User).filter(User.status == User.STATUS_ARCHIVED)

    return flask.jsonify(users=[u.getJSON() for u in users])


@api.errorhandler(404)
def not_found(e):
    return flask.jsonify(status='error', errors=['could not find resource'])


@api.route('/groups', methods=['GET'])
@requires_auth
def get_groups(session, currentUser):
    raise NotImplementedError()


@api.route('/groups', methods=['POST'])
@requires_auth
def post_groups(session, currentUser):
    raise NotImplementedError()


@api.route('/groups', methods=['DELETE'])
@requires_auth
def delete_groups(session, currentUser):
    raise NotImplementedError()


@api.route('/groups/<groupID>', methods=['GET'])
@requires_auth
def get_group(session, currentUser, groupID):
    raise NotImplementedError()


@api.route('/groups/<groupID>', methods=['PUT'])
@requires_auth
def put_group(session, currentUser, groupID):
    raise NotImplementedError()


@api.route('/groups/<groupID>', methods=['DELETE'])
@requires_auth
def delete_group(session, currentUser, groupID):
    raise NotImplementedError()


@api.route('/groups/<groupID>/users', methods=['GET'])
@requires_auth
def get_group_users(session, currentUser, groupID):
    raise NotImplementedError()


@api.route('/groups/<groupID>/users', methods=['POST'])
@requires_auth
def put_group_users(session, currentUser, groupID):
    raise NotImplementedError()


@api.route('/groups/<groupID>/users', methods=['PATCH'])
@requires_auth
def patch_group_users(session, currentUser, groupID):
    """
    PATCH users for a group; should allow for mass addition/deletion of users.
    """
    raise NotImplementedError()


@api.route('/groups/<groupID>/users/<userID>', methods=['GET'])
@requires_auth
def handle_group_users_user(session, currentUser, groupID):
    """
    GET user listing for a group.
    """
    raise NotImplementedError()


@api.route('/tests', methods=['GET'])
@requires_auth
def get_tests(session, currentUser):
    raise NotImplementedError()


@api.route('/tests', methods=['POST'])
@requires_auth
def post_tests(session, currentUser):
    raise NotImplementedError()


@api.route('/tests', methods=['DELETE'])
@requires_auth
def delete_tests(session, currentUser):
    raise NotImplementedError()
