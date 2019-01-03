from datetime import datetime

import pytest
from sanic import Sanic
from sanic_restful import marshal, fields, Api, Resource, marshal_with
from sanic_restful.marshal import marshal_with_field


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


@pytest.fixture(scope="module")
def app():
    sanic_app = Sanic(__name__)
    api = Api(sanic_app)

    class TestResource(Resource):
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

    api.add_resource(TestResource, '/')
    yield sanic_app


class TestMarshal:
    def test_marshal(self, app):
        data = {
            'name': 'bot',
            'addr1': 'fake street',
            'addr2': 'fake block',
            'city_code': 1,
            'first_names': ['Emile', 'Raoul'],
            'date_updated': datetime(2019, 1, 1),
            'date_created': datetime(2018, 1, 1),
            'id': '01',
            'boolean': False,
            'float': 1
        }
        marshal(data, resource_fields)

        request, response = app.test_client.get('/')
        assert response.status == 200

        request, response = app.test_client.post('/')
        assert response.status == 200

        request, response = app.test_client.patch('/')
        assert response.status == 200

        request, response = app.test_client.delete('/')
        assert response.status == 200
