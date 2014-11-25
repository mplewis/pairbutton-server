# http://flask.pocoo.org/docs/0.10/patterns/apierrors/


class ApiError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class InvalidUsageError(ApiError):
    status_code = 400


class UnauthorizedError(ApiError):
    status_code = 403


class NotFoundError(ApiError):
    status_code = 404


class PatchError(ApiError):
    status_code = 409
