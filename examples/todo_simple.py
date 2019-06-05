from functools import wraps

from sanic import Sanic, Blueprint
from sanic_restful import Resource, Api

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def decorator(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        return await func(request, *args, **kwargs)
    return wrapper


class TodoSimple(Resource):
    """
    You can try this example as follow:
        $ curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT
        $ curl http://localhost:5000/todo1
        {"todo1": "Remember the milk"}
        $ curl http://localhost:5000/todo2 -d "data=Change my breakpads" -X PUT
        $ curl http://localhost:5000/todo2
        {"todo2": "Change my breakpads"}

    Or from python if you have requests :
     >>> from requests import put, get
     >>> put('http://localhost:5000/todo1', data={'data': 'Remember the milk'}).json
     {u'todo1': u'Remember the milk'}
     >>> get('http://localhost:5000/todo1').json
     {u'todo1': u'Remember the milk'}
     >>> put('http://localhost:5000/todo2', data={'data': 'Change my breakpads'}).json
     {u'todo2': u'Change my breakpads'}
     >>> get('http://localhost:5000/todo2').json
     {u'todo2': u'Change my breakpads'}

    """
    method_decorators = {'get': decorator}

    async def get(self, request, todo_id):
        return {todo_id: TODOS[todo_id]}

    async def put(self, request, todo_id):
        TODOS[todo_id] = request.form.get('data')
        return {todo_id: TODOS[todo_id]}


app = Sanic(__name__)
bp = Blueprint(__name__, url_prefix='/')
api = Api(bp)

api.add_resource(TodoSimple, '/<todo_id:string>')
app.register_blueprint(bp)


if __name__ == '__main__':
    app.run(debug=True)
