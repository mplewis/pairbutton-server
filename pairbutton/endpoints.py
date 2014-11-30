from .app import db
from .models import Channel, File
from .parsers import AUTH_KEY, check_auth, createFileParser, updateFileParser
from .errors import PatchError
from .helpers import (pretty_ident, crypto_key_hex, serialize_sqla,
                      channel_with_id, file_with_id, jsonify_unsafe,
                      apply_diff, md5)

from flask import jsonify
from flask.ext.restful import Resource


class ChannelsEndpoint(Resource):
    def get(self):
        channels = db.session.query(Channel)
        channel_dicts = [serialize_sqla(c) for c in channels]
        for channel_dict in channel_dicts:
            del channel_dict['key']
        return jsonify_unsafe(channel_dicts)

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

    def delete(self, channel_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        db.session.delete(channel)
        db.session.commit()
        return '', 204


class ChannelFilesEndpoint(Resource):
    def get(self, channel_id):
        channel = channel_with_id(channel_id)
        files = channel.files
        return jsonify_unsafe([serialize_sqla(f) for f in files])

    def post(self, channel_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file_data = createFileParser.parse_args()
        file_data['channel'] = channel
        f = File(**file_data)
        db.session.add(f)
        db.session.commit()
        data_dict = serialize_sqla(f)
        del data_dict['data']
        return jsonify(data_dict)


class ChannelFileEndpoint(Resource):
    def get(self, channel_id, file_id):
        file = file_with_id(channel_id, file_id)
        return jsonify(serialize_sqla(file))

    def put(self, channel_id, file_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file = file_with_id(channel_id, file_id)
        req = updateFileParser.parse_args()
        old_data = file.data
        delta = req['file_delta']
        expected = req['expected_hash']
        new_data = apply_diff(old_data, delta)
        actual = md5(new_data)
        if expected != actual:
            raise PatchError('Couldn\'t apply patch: expected {}, got {}'
                             .format(expected, actual))
        file.data = new_data
        db.session.commit()
        return '', 204

    def delete(self, channel_id, file_id):
        channel = channel_with_id(channel_id)
        check_auth(AUTH_KEY, channel.key)
        file = file_with_id(channel_id, file_id)
        db.session.delete(file)
        db.session.commit()
        return '', 204
