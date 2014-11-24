from flask import Flask, request, jsonify
from flask.ext.restful import Resource, Api, reqparse
from flask.ext.sqlalchemy import SQLAlchemy
from Crypto.Hash import HMAC, SHA256

import random
import hashlib


AUTH_KEY = 'Auth-Key'
AUTH_SIGN = 'Auth-Signature'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

api = Api(app)


def pretty_ident(length, starts_with_consonant=True):
    consonants = [l for l in 'bdfghklmnprstvwyz']
    digraphs = ['ch', 'th', 'sh', 'ph', 'wh', 'sk']
    consonants.extend(digraphs)
    vowels = 'aeiou'
    next_is_consonant = starts_with_consonant
    out = ''
    while len(out) < length:
        if next_is_consonant:
            out += random.choice(consonants)
        else:
            out += random.choice(vowels)
        next_is_consonant = not next_is_consonant
    return out[:length]


def crypto_key_hex(bits=256):
    return hashlib.sha224(str(random.getrandbits(bits)).encode()).hexdigest()


def make_error(message, code):
    response = jsonify({'message': message})
    response.status_code = code
    return response


def channel_with_id(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first()
    if not channel:
        error = make_error('No channel with id {}'.format(channel_id), 404)
        return None, error
    else:
        return channel, None


def file_with_id(channel_id, file_id):
    channel = Channel.query.filter_by(id=channel_id).first()
    if not channel:
        error = make_error('No channel with id {}'.format(channel_id), 404)
        return None, error
    file = (File.query.filter_by(id=file_id)
            .filter_by(channel_id=channel_id).first())
    if not file:
        error = make_error('No file with id {}'.format(file_id), 404)
        return None, error
    else:
        return file, None


# http://stackoverflow.com/a/1960546/254187
def serialize_sqla(sqla):
    d = {}
    for column in sqla.__table__.columns:
        d[column.name] = str(getattr(sqla, column.name))
    return d


# https://gist.github.com/theY4Kman/3893296
def hmac_sha256(key, data):
    hash_obj = HMAC.new(key, data, SHA256)
    return hash_obj.hexdigest()


def authorized(header_name, expected):
    if header_name in request.headers:
        if request.headers[header_name] == expected:
            return True
    return False


createFileParser = reqparse.RequestParser()
createFileParser.add_argument(
    'name', type=str, required=True, location='json',
    help='name: File name is required')
createFileParser.add_argument(
    'data', type=str, required=True, location='json',
    help='data: Initial file data is required')

updateFileParser = reqparse.RequestParser()
updateFileParser.add_argument(
    'file_delta', type=str, required=True, location='json',
    help='file_delta: File diff delta is required')
updateFileParser.add_argument(
    'expected_hash', type=str, required=True, location='json',
    help='expected_hash: Hash of expected post-delta data is required')


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)
    key = db.Column(db.Text)
    files = db.relationship('File', backref='channel')

    def __init__(self, name, key):
        self.name = name
        self.key = key

    def __repr__(self):
        return '<Channel: {}, {}>'.format(self.id, self.name)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    data = db.Column(db.Text)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'),
                           nullable=False)

    def __init__(self, name, data, channel_id):
        self.name = name
        self.data = data
        self.channel_id = channel_id

    def __repr__(self):
        return ('<File: {}, {}, channel {}, {} ({} bytes)>'
                .format(self.id, self.name, self.channel.id,
                        self.data, len(self.data)))


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
        channel = Channel.query.filter_by(id=channel_id).first()
        if not authorized(AUTH_KEY, channel.key):
            return make_error('Unauthorized', 403)
        return jsonify(serialize_sqla(channel))


class ChannelFilesEndpoint(Resource):
    def get(self, channel_id):
        channel, error = channel_with_id(channel_id)
        if error:
            return error
        files = channel.files
        return jsonify(items=[serialize_sqla(f) for f in files])

    def post(self, channel_id):
        channel, error = channel_with_id(channel_id)
        if error:
            return error

        expected = hmac_sha256(channel.key.encode(), request.data)
        if not authorized(AUTH_SIGN, expected):
            return make_error('Unauthorized', 403)

        file_data = createFileParser.parse_args()
        file_data['channel_id'] = int(channel.id)
        f = File(**file_data)
        db.session.add(f)
        db.session.commit()
        return jsonify(serialize_sqla(f))


class ChannelFileEndpoint(Resource):
    def put(self, channel_id, file_id):
        channel, error = channel_with_id(channel_id)
        if error:
            return error

        expected = hmac_sha256(channel.key.encode(), request.data)
        if not authorized(AUTH_SIGN, expected):
            print(expected)
            return make_error('Unauthorized', 403)

        file, error = file_with_id(channel_id, file_id)
        if error:
            return error

        change_data = updateFileParser.parse_args()
        return jsonify(change_data)

    def delete(self, channel_id, file_id):
        channel, error = channel_with_id(channel_id)
        if error:
            return error

        expected = hmac_sha256(channel.key.encode(), request.data)
        if not authorized(AUTH_SIGN, expected):
            return make_error('Unauthorized', 403)

        file, error = file_with_id(channel_id, file_id)
        if error:
            return error

        db.session.delete(file)
        db.session.commit()
        return '', 204


api.add_resource(ChannelsEndpoint, '/channel')
api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')
api.add_resource(ChannelFileEndpoint,
                 '/channel/<string:channel_id>/file/<string:file_id>')

if __name__ == '__main__':
    app.run(debug=True)
