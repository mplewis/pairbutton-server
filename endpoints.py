from app import db
from models import Channel, File
from parsers import AUTH_KEY, check_auth, createFileParser, updateFileParser
from helpers import (pretty_ident, crypto_key_hex, serialize_sqla,
                     channel_with_id, file_with_id)

from flask import jsonify
from flask.ext.restful import Resource


class ChannelsEndpoint(Resource):
    def post(self):
        existing_channel = True
        while existing_channel:
            new_name = pretty_ident(8)
            existing_channel = Channel.query.filter_by(name=new_name).first()
        channel = Channel(new_name, crypto_key_hex())
        db.session.add(channel)
        db.session.commit()
        return jsonify(serialize_sqla(channel))


class ChannelEndpoint(Resource):
    def get(self, channel_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        return jsonify(serialize_sqla(channel))


class ChannelFilesEndpoint(Resource):
    def get(self, channel_id):
        channel = channel_with_id(channel_id)
        files = channel.files
        return jsonify(items=[serialize_sqla(f) for f in files])

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
