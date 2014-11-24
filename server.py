from app import app, api
from endpoints import (ChannelsEndpoint, ChannelEndpoint, ChannelFilesEndpoint,
                       ChannelFileEndpoint)


api.add_resource(ChannelsEndpoint, '/channel')
api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')
api.add_resource(ChannelFileEndpoint,
                 '/channel/<string:channel_id>/file/<string:file_id>')

if __name__ == '__main__':
    app.run(debug=True)
