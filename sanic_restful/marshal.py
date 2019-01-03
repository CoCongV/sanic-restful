from collections import OrderedDict
from functools import wraps

from sanic_restful import Resource
from sanic_restful.util import unpack


def marshal(data, fields, envelope=None):
    """Takes raw data (in the form of a dict, list, object) and a dict of
    fields to output and filters the data based on those fields.

    :param data: the actual object(s) from which the fields are taken from
    :param fields: a dict of whose keys will make up the final serialized
                   response output
    :param envelope: optional key that will be used to envelop the serialized
                     response


    >>> from flask_restful import fields, marshal
    >>> data = { 'a': 100, 'b': 'foo' }
    >>> mfields = { 'a': fields.Raw }

    >>> marshal(data, mfields)
    OrderedDict([('a', 100)])

    >>> marshal(data, mfields, envelope='data')
    OrderedDict([('data', OrderedDict([('a', 100)]))])

    """

    def make(cls):
        if isinstance(cls, type):
            return cls()
        return cls

    if isinstance(data, (list, tuple)):
        return (OrderedDict([(envelope, [marshal(d, fields) for d in data])])
                if envelope else [marshal(d, fields) for d in data])

    items = ((k, marshal(data, v)
              if isinstance(v, dict) else make(v).output(k, data))
             for k, v in fields.items())
    return OrderedDict(
        [(envelope, OrderedDict(items))]) if envelope else OrderedDict(items)


class marshal_with(object):
    """A decorator that apply marshalling to the return values of your methods.

    >>> from flask_restful import fields, marshal_with
    >>> mfields = { 'a': fields.Raw }
    >>> @marshal_with(mfields)
    ... def get():
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('a', 100)])

    >>> @marshal_with(mfields, envelope='data')
    ... def get():
    ...     return { 'a': 100, 'b': 'foo' }
    ...
    ...
    >>> get()
    OrderedDict([('data', OrderedDict([('a', 100)]))])

    see :meth:`flask_restful.marshal`
    """

    def __init__(self, fields, envelope=None):
        """
        :param fields: a dict of whose keys will make up the final
                       serialized response output
        :param envelope: optional key that will be used to envelop the
                        serialized response
        """
        self.fields = fields
        self.envelope = envelope

    def __call__(self, f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            _cls = args[0] if args else None
            if isinstance(_cls, Resource):
                pass
            resp = await f(*args, **kwargs)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return marshal(data, self.fields, self.envelope), code, headers
            else:
                return marshal(resp, self.fields, self.envelope)

        return wrapper


class marshal_with_field:
    """
    A decorator that formats the return values of your methods
     with a single field.

    >>> from flask_restful import marshal_with_field, fields
    >>> @marshal_with_field(fields.List(fields.Integer))
    ... def get():
    ...     return ['1', 2, 3.0]
    ...
    >>> get()
    [1, 2, 3]

    see :meth:`flask_restful.marshal_with`
    """

    def __init__(self, field):
        """
        :param field: a single field with which to marshal the output.
        """
        if isinstance(field, type):
            self.field = field()
        else:
            self.field = field

    def __call__(self, f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            resp = await f(*args, **kwargs)
            if isinstance(resp, tuple):
                data, code, headers = unpack(resp)
                return self.field.format(data), code, headers
            return self.field.format(resp)

        return wrapper
