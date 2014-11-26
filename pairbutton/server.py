from .app import create_app
from .config import DevConfig, ProdConfig
from .endpoints import (ChannelsEndpoint, ChannelEndpoint,
                        ChannelFilesEndpoint, ChannelFileEndpoint)

from flask import jsonify
from flask.ext.restful import Api

import argparse


class PairbuttonApi(Api):
    def handle_error(self, e):
        try:
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
        except Exception:  # this isn't an ApiError
            return super().handle_error(e)


parser = argparse.ArgumentParser(description='Start the Pairbutton server.')
parser.add_argument(
    '-d', '--dev', action='store_true',
    help='Start in development mode. If omitted, the server defaults to '
         'production mode.'
)
args = parser.parse_args()

if args.dev:
    curr_config = DevConfig
else:
    curr_config = ProdConfig

app = create_app(curr_config)
api = PairbuttonApi(app)

api.add_resource(ChannelsEndpoint, '/channel')
api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')
api.add_resource(ChannelFileEndpoint,
                 '/channel/<string:channel_id>/file/<string:file_id>')


if __name__ == '__main__':
    app.run()
