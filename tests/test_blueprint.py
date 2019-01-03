from sanic import Sanic, Blueprint
from sanic_restful import Api, Resource


class TestApi(Resource):
    async def get(self, request):
        return ''


class TestBlueprint:
    def test_register_blueprint(self):
        app = Sanic(__name__)
        bp = Blueprint('api', url_prefix='/api')
        api = Api(bp)
        api.add_resource(TestApi)
        app.blueprint(bp)

    def test_register_resources(self):
        bp = Blueprint('api', url_prefix='/api')
        api = Api()
        api.add_resource(TestApi)
        api.init_app(bp)
        app = Sanic(__name__)
        app.blueprint(bp)
