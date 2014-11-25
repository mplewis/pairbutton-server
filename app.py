from models import db, Channel, File

from flask import Flask
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView


def create_app(config_object):
    '''
    An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    :param config_object: The configuration object to use.
    '''
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    return app


def register_extensions(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    if app.debug:
        admin = Admin(app)
        admin.add_view(ModelView(Channel, db.session))
        admin.add_view(ModelView(File, db.session))


if __name__ == '__main__':
    print('Start the Pairbutton server with server.py, not app.py.')
