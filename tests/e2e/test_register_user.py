from uuid import uuid4

from fastapi.testclient import TestClient


def _valid_payload(**overrides: str | None) -> dict[str, str | None]:
    unique = uuid4().hex[:10]
    payload: dict[str, str | None] = {
        'username': f'user{unique}',
        'full_name': 'Juan Perez',
        'email': f'{unique}@example.com',
        'password': f'password{unique}',
    }
    payload.update(overrides)
    return payload


def test_register_user_returns_201_with_user_data_and_token(
    client: TestClient,
) -> None:
    response = client.post('/api/v1/users', json=_valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body['success'] is True
    assert body['message'] == 'Usuario registrado correctamente'
    assert body['data']['status'] == 'activo'
    assert body['data']['token']
    assert body['detail'] is None


def test_register_user_returns_409_when_username_is_already_taken(
    client: TestClient,
) -> None:
    payload = _valid_payload()
    client.post('/api/v1/users', json=payload)

    response = client.post(
        '/api/v1/users', json=_valid_payload(username=payload['username'])
    )

    assert response.status_code == 409
    body = response.json()
    assert body['success'] is False
    assert body['detail'][0]['campo'] == 'username'


def test_register_user_returns_422_when_a_required_field_is_missing(
    client: TestClient,
) -> None:
    payload = _valid_payload()
    del payload['password']

    response = client.post('/api/v1/users', json=payload)

    assert response.status_code == 422
    body = response.json()
    assert 'password' in body['message']
    assert body['detail'][0]['campo'] == 'password'


def test_register_user_returns_422_when_a_field_has_invalid_format(
    client: TestClient,
) -> None:
    response = client.post('/api/v1/users', json=_valid_payload(phone='123'))

    assert response.status_code == 422
    body = response.json()
    assert body['detail'][0]['campo'] == 'phone'
