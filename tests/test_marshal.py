from datetime import datetime

from sanic_restful import marshal, fields


resource_fields = {
    'name': fields.String,
    'address': {
        'line 1': fields.String(attribute='addr1'),
        'line 2': fields.String(attribute='addr2'),
        'city_code': fields.Integer,
    },
    'first_names': fields.List(fields.String),
    'date_updated': fields.DateTime(dt_format='rfc822'),
    'date_created': fields.DateTime(dt_format='iso8601'),
    'id': fields.Integer,
    'boolean': fields.Boolean,
    'greeting': fields.FormattedString('Hello {name}'),
    'float': fields.Float
}


class TestMarshal:
    def test_marshal(self):
        data = {
            'name': 'bot',
            'addr1': 'fake street',
            'addr2': 'fake block',
            'city_code': 1,
            'first_names': ['Emile', 'Raoul'],
            'date_updated': datetime(2019, 1, 1),
            'date_created': datetime(2018, 1, 1),
            'id': '01',
            'boolean': False,
            'float': 1
        }
        marshal(data, resource_fields)
