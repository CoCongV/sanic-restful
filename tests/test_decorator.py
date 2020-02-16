from sanic import Sanic


class TestDecorator:
    def test_decorator(self, app: Sanic):
        _, response = app.test_client.get('/login')
        assert response.status == 200
        assert response.json['message'] == 'ok'
