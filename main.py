import model
import flask
from flask import Flask
import rest
import model
import os

adminsite = flask.Blueprint('adminsite', __name__, static_folder='static')

@adminsite.route('/')
def index():
    return adminsite.send_static_file(os.path.join('html','index.html'))


@adminsite.route('/html/<path:fname>')
def html(fname):
    return adminsite.send_static_file(os.path.join('html',fname))


@adminsite.route('/js/<path:fname>')
def js(fname):
    return adminsite.send_static_file(os.path.join('js',fname))


@adminsite.route('/css/<path:fname>')
def css(fname):
    return adminsite.send_static_file(os.path.join('css',fname))


def create_app(database_uri, debug=False):
	app = Flask(__name__)
	app.debug = debug
	app.register_blueprint(rest.api, url_prefix='/api/v1.0')
	app.register_blueprint(adminsite)
	model.create_engine(database_uri, echo=debug)
	return app


if __name__ == "__main__":
	app = create_app('sqlite:///test.db?check_same_thread=False', debug=True)
	model.create_schema()
	model.create_data()
	app.run()