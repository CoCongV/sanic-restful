# needs: pip install python-simplexml
from simplexml import dumps
from sanic import Sanic
from sanic.response import HTTPResponse
from sanic_restful import Api, Resource


def output_xml(app, data, code, headers=None):
    """Makes a Flask response with a XML encoded body"""
    resp = HTTPResponse(
        dumps({
            'response': data
        }), status=code, headers=headers)
    resp.headers.extend(headers or {})
    return resp


app = Sanic(__name__)
api = Api(app, default_mediatype='application/xml')
api.representations['application/xml'] = output_xml


class Hello(Resource):
    """
        # you need requests
        >>> from requests import get
        >>> get('http://localhost:5000/me').content # default_mediatype
        '<?xml version="1.0" ?><response><hello>me</hello></response>'
        >>> get('http://localhost:5000/me', headers={"accept":"application/json"}).content
        '{"hello": "me"}'
        >>> get('http://localhost:5000/me', headers={"accept":"application/xml"}).content
        '<?xml version="1.0" ?><response><hello>me</hello></response>'
    """
    async def get(self, request, entry):
        return {'hello': entry}


api.add_resource(Hello, '/<entry:string>')

if __name__ == '__main__':
    app.run(debug=True)
