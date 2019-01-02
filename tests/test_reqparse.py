import pytest
from sanic import Sanic
from sanic_restful import Api, Resource
from sanic_restful.reqparse import RequestParser


simple_parser = RequestParser()
simple_parser.add_argument('args', location='args')
simple_parser.add_argument('form', location='form')
simple_parser.add_argument('json', location='json')

no_location_parser = RequestParser()
no_location_parser.add_argument('key')

convert_parser = RequestParser()
convert_parser.add_argument('key', type=int, location='args')
convert_parser.add_argument('key1', location='args', type=str)


@pytest.fixture(scope="module")
def app():
    sanic_app = Sanic(__name__)
    api = Api(sanic_app)

    class SimpleParserResource(Resource):
        async def post(self, request):
            args = simple_parser.parse_args(request)
            return {'args': args.args, 'form': args.form}

        async def patch(self, request):
            args = simple_parser.parse_args(request)
            return {'json': args.json}

    class NoLocation(Resource):
        async def post(self, request):
            args = no_location_parser.parse_args(request)
            assert args.key
            return {}, 200

    class Convert(Resource):
        async def get(self, request):
            args = convert_parser.parse_args(request)
            assert isinstance(args.key, int)
            assert not args.key1
            return '', 200

        async def post(self, request):
            parser = RequestParser()
            parser.add_argument('key', required=True)
            parser.parse_args(request)
            return '', 200

    api.add_resource(Convert, '/convert')
    api.add_resource(NoLocation, '/no_location')
    api.add_resource(SimpleParserResource, '/')
    yield sanic_app


class TestParse:
    def test_parse(self, app: Sanic):
        request, response = app.test_client.post(
            '/',
            params={'args': 'args'},
            data={"form": "form"})
        assert response.status == 200
        assert response.json == {
            'args': "args",
            "form": "form"
        }

    def test_no_location(self, app: Sanic):
        request, response = app.test_client.post(
            '/no_location', json={'key': 'values'})
        assert response.status == 200

    def test_convert(self, app: Sanic):
        request, response = app.test_client.get(
            '/convert', params={'key': '1'})
        assert response.status == 200

        request, response = app.test_client.post(
            '/convert')
        assert response.status == 400
