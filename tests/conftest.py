from datetime import datetime
from functools import wraps

import pytest
from sanic import Sanic
from sanic.response import json
from sanic_restful import Api, Resource, fields, marshal_with
from sanic_restful.marshal import marshal_with_field


def login_require(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        response = await func(request, *args, **kwargs)
        return response
    return wrapper


address = {
    'country': fields.String,
    'city': fields.String,
}

resource_fields = {
    'name': fields.String,
    'address': {
        'line 1': fields.String(attribute='addr1'),
        'line 2': fields.String(attribute='addr2'),
    },
    'address_region': fields.Nested(address),
    'first_names': fields.List(fields.String),
    'date_updated': fields.DateTime(dt_format='rfc822'),
    'date_created': fields.DateTime(dt_format='iso8601'),
    'id': fields.Integer,
    'boolean': fields.Boolean,
    'greeting': fields.FormattedString('Hello {name}'),
    'float': fields.Float,
    'arbitrary': fields.Arbitrary,
    'fixed': fields.Fixed,
    'none_int': fields.Integer,
}


class TestResource(Resource):
    async def get(self, request):
        return {'response': 'get'}

    async def post(self, request):
        return {'response': 'post'}

    async def put(self, request):
        return {'response': 'put'}

    async def delete(self, request):
        return {'response': 'delete'}

    async def patch(self, request):
        return {'response': 'patch'}


class TestResponse(Resource):
    async def get(self, request):
        return json({'response': 'get'})


class TestLogin(Resource):

    method_decorators = {"get": login_require}

    async def get(self, request):
        return {'message': 'ok'}


class TestMarshal(Resource):

    @marshal_with_field(fields.List(fields.Integer))
    async def get(self, request):
        return ['1', 2, 3.0], 200, {}

    @marshal_with_field(fields.List(fields.Integer))
    async def delete(self, request):
        return ['1', 2, 3.0]

    @marshal_with(resource_fields)
    async def post(self, request):
        data = {
            'name': 'bot',
            'line1': 'fake street',
            'line2': 'fake block',
            'city': 1,
            'country': 'China',
            'first_names': ['Emile', 'Raoul'],
            'date_updated': datetime(2019, 1, 1),
            'date_created': datetime(2018, 1, 1),
            'id': '01',
            'boolean': False,
            'float': 1,
            'arbitrary': 634271127864378216478362784632784678324.23432,
            'fixed': 23432,
            'none_int': None
        }
        return data

    @marshal_with(resource_fields)
    async def patch(self, request):
        data = {
            'name': 'bot',
            'line1': 'fake street',
            'line2': 'fake block',
            'city': 1,
            'country': 'China',
            'first_names': ['Emile', 'Raoul'],
            'date_updated': datetime(2019, 1, 1),
            'date_created': datetime(2018, 1, 1),
            'id': '01',
            'boolean': False,
            'float': 1,
            'arbitrary': 634271127864378216478362784632784678324.23432,
            'fixed': 23432,
            'none_int': None
        }
        return data, 200, {}


@pytest.fixture(scope="session", autouse=True)
def app():
    sanic_app = Sanic("test")
    api = Api(sanic_app)

    api.add_resource(TestResource, '/')
    api.add_resource(TestResponse, '/response')
    api.add_resource(TestLogin, '/login')
    api.add_resource(TestMarshal, '/marshal')
    yield sanic_app
