from .models import Channel, File
from .errors import NotFoundError, PatchError

from flask import jsonify, Response
from diff_match_patch import diff_match_patch

import random
import hashlib
import json


dmp = diff_match_patch()


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
        raise NotFoundError('No channel with ID: {}'.format(channel_id))
    return channel


def file_with_id(channel_id, file_id):
    channel_with_id(channel_id)  # verify channel exists
    file = (File.query.filter_by(id=file_id)
            .filter_by(channel_id=channel_id).first())
    if not file:
        raise NotFoundError('No file with ID: {}'.format(file_id))
    return file


# http://stackoverflow.com/a/1960546/254187
def serialize_sqla(sqla):
    d = {}
    for column in sqla.__table__.columns:
        d[column.name] = str(getattr(sqla, column.name))
    return d


def jsonify_unsafe(array):
    json_str = json.dumps(array)
    resp = Response(json_str, mimetype='application/json')
    return resp


def diff(old_data, new_data):
    patches = dmp.patch_make(old_data, new_data)
    return dmp.patch_toText(patches)


def apply_diff(old_data, delta):
    patches = dmp.patch_fromText(delta)
    new_data, success = dmp.patch_apply(patches, old_data)
    if not all(success):
        success_count = len([x for x in success if x])
        raise PatchError('Patching failed: {}/{} successes'
                         .format(success_count, len(success)))
    return new_data


def md5(data):
    m = hashlib.md5()
    m.update(data.encode())
    return m.hexdigest()
