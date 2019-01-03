from datetime import datetime

import pytest
from sanic import Sanic
from sanic_restful import Api, Resource, marshal_with, fields


resource_fields = {
    'name': fields.String,
    'address': fields.String,
    'date_updated': fields.DateTime(dt_format='rfc822'),
}


@pytest.fixture(scope="module")
def app():
    sanic_app = Sanic(__name__)
    api = Api(sanic_app)

    class TestApi(Resource):
        @marshal_with(resource_fields, envelope="data")
        async def get(self, request):
            return {
                'name': 1,
                'address': '192.168.1.1',
                'date_updated': datetime(year=2019, month=1, day=1)
            }

    api.add_resource(TestApi, '/')
    yield sanic_app


class TestMarshal:
    def test_marshal(self, app):
        request, response = app.test_client.get('/')
        assert response.status == 200
        assert response.json == {
            'data': {
                'name': '1',
                'date_updated': 'Tue, 01 Jan 2019 00:00:00 -0000',
                'address': '192.168.1.1'
            }
        }
