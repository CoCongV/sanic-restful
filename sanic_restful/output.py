from functools import partial
from json import dumps

from sanic.response import HTTPResponse

json_dumps = partial(dumps, separators=(",", ":"))


def output_json(app, data, code, headers=None):
    settings = app.config.get('RESTFUL_JSON', {})
    dumps = settings.pop('JSON_DUMP', None) or json_dumps
    # If we're in debug mode, and the indent is not set, we set it to a
    # reasonable value here.  Note that this won't override any existing value
    # that was set.  We also set the "sort_keys" value.
    if app.debug:
        settings.setdefault('indent', 4)

    return HTTPResponse(
        dumps(data, **settings) + "\n",
        headers=headers,
        status=200,
        content_type="application/json",
    )
