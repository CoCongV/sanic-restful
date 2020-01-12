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
convert_parser.add_argument('key2', type=str, trim=True, case_sensitive=True)
convert_parser.add_argument(
    'key3', type=str, default='default_value', dest='default_key')


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
            return {"key": args.key}, 200, {}

    class Convert(Resource):
        async def get(self, request):
            args = convert_parser.parse_args(request)
            assert isinstance(args.key, int)
            assert not args.key1
            assert args.key2 == 'VALUE'
            assert args.default_key == 'default_value'
            return '', 200

        async def post(self, request):
            parser = RequestParser()
            parser.add_argument('key', required=True)
            parser.parse_args(request)
            return '',

    class ParserChoices(Resource):
        async def get(self, request):
            choices = ('one', 'two')
            parser = RequestParser()
            parser.add_argument(
                'foo', choices=choices, help="bad choice: {error_msg}")
            args = parser.parse_args(request)
            assert args.foo in choices
            return ''

    class StrictParse(Resource):
        async def get(self, request):
            parser = RequestParser()
            parser.add_argument('key')
            parser.parse_args(request, True)
            return ''

    class TrimParse(Resource):
        async def get(self, request):
            parser = RequestParser(trim=True)
            parser.add_argument('key')
            args = parser.parse_args(request)
            assert args.key == 'value'
            return ''

    class NullParse(Resource):
        async def post(self, request):
            parser = RequestParser()
            parser.add_argument('key', nullable=False, location='json')
            parser.parse_args(request)
            return ''

        async def put(self, request):
            parser = RequestParser()
            parser.add_argument('key', nullable=True, location='json')
            parser.parse_args(request)
            return ''

    api.add_resource(NullParse, '/null')
    api.add_resource(TrimParse, '/trim')
    api.add_resource(StrictParse, '/strict')
    api.add_resource(ParserChoices, '/choices')
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
        assert response.json == {
            'key': 'values'
        }

    def test_convert(self, app: Sanic):
        request, response = app.test_client.get(
            '/convert', params={'key': '1', 'key2': 'VALUE'})
        assert response.status == 200

        request, response = app.test_client.post(
            '/convert')
        assert response.status == 400

    def test_parser_action(self):
        parser = RequestParser()
        parser.add_argument('key', default='value', dest='key0')
        parser.copy()
        parser.replace_argument('key', default='value1', dest='key0')
        parser.remove_argument('key')

    def test_parser_choice(self, app):
        request, response = app.test_client.get(
            '/choices', params={'foo': 'one'})
        assert response.status == 200
        request, response = app.test_client.get(
            '/choices', params={'foo': 'zero'})
        assert response.status == 400

    def test_parser_strict(self, app):
        request, response = app.test_client.get(
            '/strict', params={
                'key': 'value',
                'other_key': 'other_value'
            })
        assert response.status == 400

    def test_parser_trim(self, app):
        request, response = app.test_client.get(
            '/trim', params={'key': '  value  '})
        assert response.status == 200

    def test_null_parser(self, app):
        requst, response = app.test_client.post(
            '/null', json={'key': None})
        assert response.status == 400
        request, response = app.test_client.put('/null', json={'key': None})
        assert response.status == 200
