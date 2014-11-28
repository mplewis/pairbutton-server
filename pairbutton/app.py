from .models import db, Channel, File
from .endpoints import (ChannelsEndpoint, ChannelEndpoint,
                        ChannelFilesEndpoint, ChannelFileEndpoint)

from flask import Flask, jsonify
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.restful import Api


class PairbuttonApi(Api):
    def handle_error(self, e):
        try:
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
        except Exception:  # this isn't an ApiError
            return super().handle_error(e)


def create_app(config_object):
    """
    An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)
    register_api(app)
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


def register_api(app):
    api = PairbuttonApi(app)
    api.add_resource(ChannelsEndpoint, '/channel')
    api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
    api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')
    api.add_resource(ChannelFileEndpoint,
                     '/channel/<string:channel_id>/file/<string:file_id>')


if __name__ == '__main__':
    print('Start the Pairbutton server with server.py, not app.py.')
