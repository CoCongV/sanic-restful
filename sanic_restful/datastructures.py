from collections import UserDict, defaultdict


class TypeConversionDict(UserDict):

    def get(self, key, default=None, type=None):
        try:
            rv = self[key]
        except KeyError:
            return default
        if type is not None:
            try:
                rv = type(rv)
            except ValueError:
                rv = default
        return rv


class MultiDict(TypeConversionDict):
    def __init__(self, mapping=None):
        tmp = defaultdict(list)
        for key, value in mapping or ():
            tmp[key].append(value)
        super().__init(self, tmp)
