from sanic import Sanic
from sanic.exceptions import NotFound, Unauthorized
from sanic.log import error_logger
from sanic_restful import reqparse, Api, Resource

app = Sanic(__name__)
errors = {
    'TypeError': {
        'status': 404,
        'message': 'not found'
    }
}
api = Api(app, errors=errors)


TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        raise NotFound(message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', location='form')
parser.add_argument('test', location='json')

post_parser = reqparse.RequestParser()
post_parser.add_argument('key')
# post_parser.add_argument("value")

# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    async def get(self, request, todo_id):
        raise NotFound('hahaha')
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    async def delete(self, request, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    async def put(self, request, todo_id):
        args = parser.parse_args(request)
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201

    async def patch(self, request, todo_id):
        raise Unauthorized('fail')


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    async def get(self, request):
        return TODOS

    async def post(self, request):
        args = parser.parse_args(request)
        error_logger.info(type(request.json.get('test')))
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


class TodoArgs(Resource):
    async def post(self, request):
        args = post_parser.parse_args(request)
        TODOS[args.key] = args.value
        return TODOS


# Actually setup the Api resource routing here
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id:string>')
api.add_resource(TodoArgs, '/todos/args')


if __name__ == '__main__':
    app.run(debug=True)
