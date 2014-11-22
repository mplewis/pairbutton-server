from flask import Flask, request, jsonify
from flask.ext.restful import Resource, Api, reqparse
from flask.ext.sqlalchemy import SQLAlchemy

import random
import hashlib


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
    response = jsonify({'error': message})
    response.status_code = code
    return response


def channel_with_id(channel_id):
    channel = Channel.query.filter_by(id=channel_id).first()
    if not channel:
        error = make_error('No channel with id {}'.format(channel_id), 404)
        return None, error
    else:
        return channel, None


# http://stackoverflow.com/a/1960546/254187
def serialize_sqla(sqla):
    d = {}
    for column in sqla.__table__.columns:
        d[column.name] = str(getattr(sqla, column.name))
    return d


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
        return jsonify(serialize_sqla(channel))


newFileParser = reqparse.RequestParser()
newFileParser.add_argument('name', type=str,
                           help='name: File name is required',
                           required=True, location='json')
newFileParser.add_argument('data', type=str,
                           help='data: Initial file data is required',
                           required=True, location='json')


class ChannelFilesEndpoint(Resource):
    def get(self, channel_id):
        channel, error = channel_with_id(channel_id)
        if error:
            return error
        files = channel.files
        return jsonify(items=[serialize_sqla(f) for f in files])

    def post(self, channel_id):
        channel, error = channel_with_id(channel_id)
        print(channel)
        if error:
            return error
        file_data = newFileParser.parse_args()
        file_data['channel_id'] = int(channel.id)
        f = File(**file_data)
        db.session.add(f)
        db.session.commit()
        return jsonify(serialize_sqla(f))


api.add_resource(ChannelsEndpoint, '/channel')
api.add_resource(ChannelEndpoint, '/channel/<string:channel_id>')
api.add_resource(ChannelFilesEndpoint, '/channel/<string:channel_id>/file')

if __name__ == '__main__':
    app.run(debug=True)
