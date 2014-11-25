from app import create_app
from config import DevConfig, ProdConfig
from endpoints import (ChannelsEndpoint, ChannelEndpoint, ChannelFilesEndpoint,
                       ChannelFileEndpoint)

from flask.ext.restful import Api

import argparse


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
api = Api(app)

api.add_resource(ChannelsEndpoint, '/channel')
api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')
api.add_resource(ChannelFileEndpoint,
                 '/channel/<string:channel_id>/file/<string:file_id>')

if __name__ == '__main__':
    app.run()
