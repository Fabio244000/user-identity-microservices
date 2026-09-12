from fastapi.testclient import TestClient


def test_health_returns_ok_with_database_connected(client: TestClient) -> None:
    response = client.get('/health')

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data'] == {'database': 'ok'}
