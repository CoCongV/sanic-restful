from collections import OrderedDict
from functools import wraps

from sanic import Blueprint, Sanic
from sanic.exceptions import ServerError
from sanic.response import BaseHTTPResponse, text
from sanic_restful.exceptions import NotAcceptable
from sanic_restful.output import output_json
from sanic_restful.util import unpack

from werkzeug.http import parse_accept_header

DEFAULT_REPRESENTATIONS = [
    ('application/json', output_json)
]


class Api:
    """
    The main entry point for the application.
    You need to initialize it with a Flask Application: ::

    >>> app = Flask(__name__)
    >>> api = restful.Api(app)

    Alternatively, you can use :meth:`init_app` to set the Flask application
    after it has been constructed.

    :param app: the Flask application object
    :type app: flask.Flask or flask.Blueprint
    :param prefix: Prefix all routes with a value, eg v1 or 2010-04-01
    :type prefix: str
    :param default_mediatype: The default media type to return
    :type default_mediatype: str
    :param decorators: Decorators to attach to every resource
    :type decorators: list
    :param catch_all_404s: Use :meth:`handle_error`
        to handle 404 errors throughout your app
    :param serve_challenge_on_401: Whether to serve a challenge response to
        clients on receiving 401. This usually leads to a username/password
        popup in web browers.
    :param url_part_order: A string that controls the order that the pieces
        of the url are concatenated when the full url is constructed.  'b'
        is the blueprint (or blueprint registration) prefix, 'a' is the api
        prefix, and 'e' is the path component the endpoint is added with
    :type catch_all_404s: bool
    :param errors: A dictionary to define a custom response for each
        exception or error raised during a request
    :type errors: dict

    """

    def __init__(self,
                 app=None,
                 prefix='',
                 default_mediatype="application/json",
                 decorators=None,
                 catch_all_404s=False,
                 serve_challenge_on_401=False,
                 url_part_order="bae",
                 errors=None):
        self.representations = OrderedDict(DEFAULT_REPRESENTATIONS)
        self.urls = {}
        self.prefix = prefix
        self.default_mediatype = default_mediatype
        self.decorators = decorators if decorators else []
        self.catch_all_404s = catch_all_404s
        self.serve_challenge_on_401 = serve_challenge_on_401
        self.url_part_order = url_part_order
        self.errors = errors or {}
        self.blueprint_setup = None
        self.endpoints = set()
        self.resources = []
        self.app = None
        self.blueprint = None

        if app:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        """Initialize this class with the given :class:`flask.Flask`
        application or :class:`flask.Blueprint` object.

        :param app: the Flask application or blueprint object

        Examples::

            api = Api()
            api.add_resource(...)
            api.init_app(app)

        """
        # If app is a blueprint, defer the initialization
        if isinstance(app, Blueprint):
            # self.blueprint = app
            self._bp_register = app.register
            # TODO: register api resource for bp that call add resource function
            app.register = self._sanic_blueprint_register_hook(app)
        elif isinstance(app, Sanic):
            self.register_api(app)
        else:
            raise TypeError("only support sanic object and blupirint")

    def _sanic_blueprint_register_hook(self, bp: Blueprint):
        def register(app, options):
            bp_obj = self._bp_register(app, options)
            self.register_api(bp)
            return bp_obj
        return register

    def register_api(self, app):
        if len(self.resources) > 0:
            for resource, urls, kwargs in self.resources:
                self._register_view(app, resource, *urls, **kwargs)

    def _register_view(self, app, resource, *urls, **kwargs):
        endpoint = kwargs.pop("endpoint", None) or resource.__name__.lower()
        self.endpoints.add(endpoint)
        resource_class_args = kwargs.pop("resource_class_args", ())
        resource_class_kwargs = kwargs.pop("resource_class_kwargs", {})

        # Why?
        # resouce.mediatypes = self.mediatypes
        resource.endpoint = endpoint
        resource_func = self.output(
            resource.as_view(self, *resource_class_args,
                             **resource_class_kwargs))

        for decorator in self.decorators:
            resource_func = decorator(resource_func)

        for url in urls:
            rule = self._complete_url(url, '')
            # Add the url to the application or blueprint
            app.add_route(uri=rule, handler=resource_func, **kwargs)

    @property
    def mediatypes(self):
        return [
            "application/json",
            "text/plain; charset=utf-8",
            "application/octet-stream",
            "text/html; charset=utf-8",
        ]

    def output(self, resource):
        """Wraps a resource (as a flask view function), for cases where the
        resource does not directly return a response object

        :param resource: The resource as a flask view function
        """
        @wraps(resource)
        async def wrapper(request, *args, **kwargs):
            resp = await resource(request, *args, **kwargs)
            if isinstance(resp, BaseHTTPResponse):
                return resp
            else:
                data, code, headers = unpack(resp)
            return self.make_response(request, data, code, headers=headers)
        return wrapper

    def make_response(self, request, data, *args, **kwargs):
        """Looks up the representation transformer for the requested media
        type, invoking the transformer to create a response object. This
        defaults to default_mediatype if no transformer is found for the
        requested mediatype. If default_mediatype is None, a 406 Not
        Acceptable response will be sent as per RFC 2616 section 14.1

        :param data: Python object containing response data to be transformed
        """
        default_mediatype = kwargs.pop("fallback_mediatype",
                                       None) or self.default_mediatype
        # mediatype = best_match_accept_mimetype(
        #     request, self.representations, default=default_mediatype)
        mediatype = parse_accept_header(request.headers.get(
            'accept', None)).best_match(
                self.representations, default=default_mediatype)
        if not mediatype:
            raise NotAcceptable("Not Acceptable")
        if mediatype in self.representations:
            resp = self.representations[mediatype](request.app, data, *args,
                                                   **kwargs)
            resp.headers["Content-type"] = mediatype
            return resp
        elif mediatype == "text/plain":
            resp = text(str(data), *args, **kwargs)
            return resp
        else:
            raise ServerError(None)

    def _complete_url(self, url_part, registration_prefix):
        """This method is used to defer the construction of the final url in
        the case that the Api is created with a Blueprint.

        :param url_part: The part of the url the endpoint is registered with
        :param registration_prefix: The part of the url contributed by the
            blueprint.  Generally speaking, BlueprintSetupState.url_prefix
        """
        parts = {'b': registration_prefix, 'a': self.prefix, 'e': url_part}
        return ''.join(parts[key] for key in self.url_part_order if parts[key])

    def add_resource(self, resource, *urls, **kwargs):
        """Adds a resource to the api.

        :param resource: the class name of your resource
        :type resource: :class:`Resource`

        :param urls: one or more url routes to match for the resource, standard
                     flask routing rules apply.  Any url variables will be
                     passed to the resource method as args.
        :type urls: str

        :param endpoint: endpoint name
            (defaults to :meth:`Resource.__name__.lower`
            Can be used to reference this route in :class:`fields.Url` fields
        :type endpoint: str

        :param resource_class_args: args to be forwarded to the constructor of
            the resource.
        :type resource_class_args: tuple

        :param resource_class_kwargs: kwargs to be forwarded to the constructor
            of the resource.
        :type resource_class_kwargs: dict

        Additional keyword arguments not specified above will be passed as-is
        to :meth:`flask.Flask.add_url_rule`.

        Examples::

            api.add_resource(HelloWorld, '/', '/hello')
            api.add_resource(Foo, '/foo', endpoint="foo")
            api.add_resource(FooSpecial, '/special/foo', endpoint="foo")

        """
        if self.app:
            self._register_view(self.app, resource, *urls, **kwargs)
        else:
            self.resources.append((resource, urls, kwargs))

    def resource(self, *urls, **kwargs):
        """Wraps a :class:`~flask_restful.Resource` class, adding it to the
        api. Parameters are the same as :meth:`~flask_restful.Api.add_resource`

        Example::

            app = Flask(__name__)
            api = restful.Api(app)

            @api.resource('/foo')
            class Foo(Resource):
                def get(self):
                    return 'Hello, World!'

        """

        def decorator(cls):
            self.add_resource(cls, *urls, **kwargs)
            return cls

        return decorator

    def representation(self, mediatype):
        """Allows additional representation transformers to be declared for the
        api. Transformers are functions that must be decorated with this
        method, passing the mediatype the transformer represents. Three
        arguments are passed to the transformer:

        * The data to be represented in the response body
        * The http status code
        * A dictionary of headers

        The transformer should convert the data appropriately for the mediatype
        and return a Flask response object.

        Ex::

            @api.representation('application/xml')
            def xml(data, code, headers):
                resp = make_response(convert_data_to_xml(data), code)
                resp.headers.extend(headers)
                return resp
        """

        def wrapper(func):
            self.representations[mediatype] = func
            return func

        return wrapper
