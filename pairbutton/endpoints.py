from .app import db
from .models import Channel, File
from .parsers import AUTH_KEY, check_auth, createFileParser, updateFileParser
from .helpers import (pretty_ident, crypto_key_hex, serialize_sqla,
                      channel_with_id, file_with_id, jsonify_unsafe)

from flask import jsonify
from flask.ext.restful import Resource


class ChannelsEndpoint(Resource):
    def get(self):
        channels = db.session.query(Channel)
        return jsonify_unsafe([serialize_sqla(c) for c in channels])

    def post(self):
        while True:
            new_name = pretty_ident(8)
            existing = Channel.query.filter_by(name=new_name).first()
            if not existing:
                break
        channel = Channel(new_name, crypto_key_hex())
        db.session.add(channel)
        db.session.commit()
        return jsonify(serialize_sqla(channel))


class ChannelEndpoint(Resource):
    def get(self, channel_id):
        channel = channel_with_id(channel_id)
        channel_info = serialize_sqla(channel)
        del channel_info['key']
        return jsonify(channel_info)


class ChannelFilesEndpoint(Resource):
    def get(self, channel_id):
        channel = channel_with_id(channel_id)
        files = channel.files
        return jsonify_unsafe([serialize_sqla(f) for f in files])

    def post(self, channel_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file_data = createFileParser.parse_args()
        file_data['channel_id'] = int(channel.id)
        f = File(**file_data)
        db.session.add(f)
        db.session.commit()
        return jsonify(serialize_sqla(f))


class ChannelFileEndpoint(Resource):
    def get(self, channel_id, file_id):
        file = file_with_id(channel_id, file_id)
        return jsonify(serialize_sqla(file))

    def put(self, channel_id, file_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file = file_with_id(channel_id, file_id)
        change_data = updateFileParser.parse_args()
        return jsonify(change_data)

    def delete(self, channel_id, file_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file = file_with_id(channel_id, file_id)
        db.session.delete(file)
        db.session.commit()
        return '', 204
