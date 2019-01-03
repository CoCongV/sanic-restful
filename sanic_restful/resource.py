from collections import OrderedDict, Mapping, Sequence

from sanic.request import Request
from sanic.response import BaseHTTPResponse
from sanic.views import HTTPMethodView
from sanic_restful.util import best_match_accept_mimetype, unpack


class Resource(HTTPMethodView):
    """
    Represents an abstract RESTful resource. Concrete resources should
    extend from this class and expose methods for each supported HTTP
    method. If a resource is invoked with an unsupported HTTP method,
    the API will return a response with status 405 Method Not Allowed.
    Otherwise the appropriate method is called and passed all arguments
    from the url rule used when adding the resource to an Api instance. See
    :meth:`~sanic_restful.Api.add_resource` for details.

    :param method_decorators: Mapping class; if you need use Sequence,
        use decorators attribute.
        example:
            method_decorators = {'get': login_require}
            method_decoratros = {'get': [permission, login_require]}
    """
    representations = None
    method_decorators = {}

    def __init__(self, request: Request, *args, **kwargs):
        self.request = request

    async def dispatch_request(self, request: Request, *args, **kwargs):
        method = request.method.lower()
        handler = getattr(self, method, None)

        # if not handler and request.method == "head":
        #     handler = getattr(self, "get", None)
        # assert handler is not None, 'Unimplemented method %r' % request.method

        if self.method_decorators:
            for decorator in self.method_decorators.get(method, []):
                handler = decorator(handler)

        resp = await handler(request, *args, **kwargs)
        if isinstance(resp, BaseHTTPResponse):
            return resp

        representations = self.representations or OrderedDict()

        mediatype = best_match_accept_mimetype(
            request, representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
        return resp

    @classmethod
    def as_view(cls, *class_args, **class_kwargs):
        """Return view function for use with the routing system, that
        dispatches request to appropriate handler method.
        """
        if cls.method_decorators:
            if not isinstance(cls.method_decorators, Mapping):
                raise TypeError("method_decorators must be Mapping")
            for method, decorators in cls.method_decorators.items():
                if not isinstance(decorators, Sequence):
                    cls.method_decorators[method] = [decorators]

        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        view.view_class = cls
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__name__ = cls.__name__
        return view
