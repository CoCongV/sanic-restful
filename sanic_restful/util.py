from collections import OrderedDict


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}
    value_len = len(value)
    if value_len == 2:
        return value[0], value[1], {}
    elif value_len == 3:
        return value[0], value[1], value[2]
    else:
        return value, 200, {}


def get_accept_mimetypes(request):
    accept_types = request.headers.get('accept', None)
    if accept_types is None:
        return {}
    split_types = str(accept_types).split(',')
    # keep the order they appear!
    return OrderedDict([((s, 1,), s,) for s in split_types])


def best_match_accept_mimetype(request, representations, default=None):
    if representations is None or len(representations) < 1:
        return default
    try:
        accept_mimetypes = get_accept_mimetypes(request)
        if accept_mimetypes is None or len(accept_mimetypes) < 1:
            return default
        # find exact matches, in the order they appear in the `Accept:` header
        for accept_type, qual in accept_mimetypes:
            if accept_type in representations:
                return accept_type
        # match special types, like "application/json;charset=utf8" where the first half matches.
        for accept_type, qual in accept_mimetypes:
            type_part = str(accept_type).split(';', 1)[0]
            if type_part in representations:
                return type_part
        # if _none_ of those don't match, then fallback to wildcard matching
        for accept_type, qual in accept_mimetypes:
            if accept_type == "*"\
               or accept_type == "*/*"\
               or accept_type == "*.*":
                return default
    except (AttributeError, KeyError):
        return default
