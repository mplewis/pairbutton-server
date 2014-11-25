from flask import request
from flask.ext.restful import reqparse


AUTH_KEY = 'Auth-Key'


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
