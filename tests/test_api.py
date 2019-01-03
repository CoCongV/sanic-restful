import pytest
from sanic import Sanic
from sanic.response import json
from sanic_restful import Api, Resource


@pytest.fixture(scope="module")
def app():
    sanic_app = Sanic(__name__)
    api = Api(sanic_app)

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

    api.add_resource(TestResponse, '/response')
    api.add_resource(TestResource, '/')
    yield sanic_app


class TestAPI:

    def test_api(self, app: Sanic):
        request, response = app.test_client.get('/', debug=True)
        assert response.status == 200
        assert response.json['response'] == 'get'

        request, response = app.test_client.post('/')
        assert response.status == 200
        assert response.json['response'] == 'post'

        request, response = app.test_client.put('/')
        assert response.status == 200
        assert response.json['response'] == 'put'

        request, response = app.test_client.delete('/')
        assert response.status == 200
        assert response.json['response'] == 'delete'

        request, response = app.test_client.patch('/')
        assert response.status == 200
        assert response.json['response'] == 'patch'

        request, response = app.test_client.head('/')
        assert response.status == 405

        request, response = app.test_client.get('/response')
        assert response.status == 200
        assert response.json['response'] == 'get'
