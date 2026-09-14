from uuid import uuid4

from fastapi.testclient import TestClient


def _register_and_get_token(client: TestClient) -> str:
    unique = uuid4().hex[:10]
    payload = {
        'username': f'user{unique}',
        'full_name': 'Juan Perez',
        'email': f'{unique}@example.com',
        'password': f'password{unique}',
    }
    response = client.post('/api/v1/users', json=payload)
    token: str = response.json()['data']['token']
    return token


def test_close_session_returns_200_and_closes_the_session(client: TestClient) -> None:
    token = _register_and_get_token(client)

    response = client.post(
        '/api/v1/logout', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['message'] == 'Sesión cerrada exitosamente.'
    assert body['data'] is None


def test_close_session_returns_401_when_session_already_closed(
    client: TestClient,
) -> None:
    token = _register_and_get_token(client)
    client.post('/api/v1/logout', headers={'Authorization': f'Bearer {token}'})

    response = client.post(
        '/api/v1/logout', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 401
    body = response.json()
    assert body['success'] is False


def test_close_session_returns_401_for_a_malformed_token(client: TestClient) -> None:
    response = client.post(
        '/api/v1/logout', headers={'Authorization': 'Bearer not-a-real-token'}
    )

    assert response.status_code == 401
