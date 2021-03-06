from sanic import Sanic


class TestAPI:

    def test_api(self, app: Sanic):
        request, response = app.test_client.get('/', debug=True)
        assert response.status == 200
        assert response.json['response'] == 'get'

        request, response = app.test_client.post('/')
        assert response.status == 200
        assert response.json['response'] == 'post'

        request, response = app.test_client.put('/')
        assert response.status == 200
        assert response.json['response'] == 'put'

        request, response = app.test_client.delete('/')
        assert response.status == 200
        assert response.json['response'] == 'delete'

        request, response = app.test_client.patch('/')
        assert response.status == 200
        assert response.json['response'] == 'patch'

        request, response = app.test_client.head('/')
        assert response.status == 405

        request, response = app.test_client.get('/response')
        assert response.status == 200
        assert response.json['response'] == 'get'
