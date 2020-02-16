from datetime import datetime

from sanic_restful import fields, marshal


address = {
    'country': fields.String,
    'city': fields.String,
}

resource_fields = {
    'name': fields.String,
    'address': {
        'line 1': fields.String(attribute='addr1'),
        'line 2': fields.String(attribute='addr2'),
    },
    'address_region': fields.Nested(address), 
    'first_names': fields.List(fields.String),
    'date_updated': fields.DateTime(dt_format='rfc822'),
    'date_created': fields.DateTime(dt_format='iso8601'),
    'id': fields.Integer,
    'boolean': fields.Boolean,
    'greeting': fields.FormattedString('Hello {name}'),
    'float': fields.Float,
    'arbitrary': fields.Arbitrary,
    'fixed': fields.Fixed,
    'none_int': fields.Integer,
}


class TestMarshal:
    def test_marshal(self, app):
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
        url = '/marshal'

        _, response = app.test_client.get(url)
        assert response.status == 200

        _, response = app.test_client.post(url)
        assert response.status == 200

        _, response = app.test_client.patch(url)
        assert response.status == 200

        _, response = app.test_client.delete(url)
        assert response.status == 200
