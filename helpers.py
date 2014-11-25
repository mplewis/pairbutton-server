from models import Channel, File

from flask import jsonify
from Crypto.Hash import HMAC, SHA256

import random
import hashlib


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
