[![Build Status](https://travis-ci.org/CoCongV/sanic-restful.svg?branch=develop)](https://travis-ci.org/CoCongV/sanic-restful)
[![codebeat badge](https://codebeat.co/badges/05407b18-a508-4cde-ac35-8e6776ea20e1)](https://codebeat.co/projects/github-com-cocongv-sanic-restful-develop)
[![Maintainability](https://api.codeclimate.com/v1/badges/bb199b737ab079fd7b0c/maintainability)](https://codeclimate.com/github/CoCongV/sanic-restful/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/bb199b737ab079fd7b0c/test_coverage)](https://codeclimate.com/github/CoCongV/sanic-restful/test_coverage)
[![PyPI version](https://badge.fury.io/py/sanic-restful.svg)](https://badge.fury.io/py/sanic-restful)
[![](https://img.shields.io/badge/python-3.6-blue.svg)](https://pypi.org/project/sanic-restful/)
# Sanic-RESTful

Sanic-RESTful is an extension for Sanic that adds support for quickly building REST APIs.
It is a lightweight abstraction that works with your existing ORM/libraries.
Sanic-RESTful encourage best practices with minimal setup.
if you are familiar with Sanic, Sanic-RESTful should be easy to pick up.
It provides a coherent collection of decorators and tools to describe your API

## Note
There are still references to modules from Flask and Werkzeug in the repo.
But It work fine now.

## Compatibility
Sanic-RESTful requires Python 3.6+

## Installtion
```
pip install sanic-restful
```
## Quick start
With Sanic-RESTful, you only import the api instance to route or sanic class instance,
and document your endpoints
Example (class-view):
```python
from sanic import Sanic
from sanic_restful import Api, Resource, reqparse

app = Sanic(__name__)
api = Api(app, errors=errors)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}

parser = reqparse.RequestParser()
parser.add_argument('id', location=form)


class Todo(Resource):
    async def get(self, request, to_id):
        return TODOS[to_id]

    async def delete(self, request, todo_id):
        del TODOS[todo_id]
        return '', 204

    async def put(self, request, todo_id):
        args = parser.parse_args(request)
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201

    async def patch(self, request, todo_id):
        raise Unauthorized('Fail')


api.add_resource(Todo, '/todos/<todo_id:string>')

if __name__ == '__main__':
    app.run(debug=True)
```

Decorators example:
```python
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
        print(type(request))
        request.user = 'User'
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
bp = Blueprint(__name__, url_prefix='/test')
api = Api(bp)

api.add_resource(TodoSimple, '/<todo_id:string')
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
```
Note: Sanic-RESTful is different with Flask-RESTful, Must be "async"  that decoratored function.
Otherwise, The app will raise "TypeError: xxxx can't be used in 'await' expression"

## User Guide

This part of the documention will show you how to get started in using Sanic-RESTful with Sanic [here](https://flask-restful.readthedocs.io/)


## Additional Notes

### Running the Tests

```
python setup.py test
```

### PYPI
[Sanic-RESTful @ PyPI](https://pypi.org/project/sanic-restful/)
