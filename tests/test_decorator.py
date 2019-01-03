from functools import wraps

import pytest
from sanic import Sanic
from sanic_restful import Api, Resource


@pytest.fixture(scope="module")
def app():
    sanic_app = Sanic(__name__)
    api = Api(sanic_app)

    def login_require(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            response = await func(request, *args, **kwargs)
            return response
        return wrapper

    class TestApi(Resource):
        method_decorators = {'get': login_require}

        async def get(self, request):
            return ''

    api.add_resource(TestApi, '/')
    yield sanic_app


class TestDecorator:
    def test_decorator(self, app: Sanic):
        request, response = app.test_client.get('/')
        assert response.status == 200
