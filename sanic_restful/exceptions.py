from sanic.exceptions import SanicException, add_status_code


@add_status_code(405)
class MethodNotAllowed(SanicException):
    pass


@add_status_code(406)
class NotAcceptable(SanicException):
    pass
