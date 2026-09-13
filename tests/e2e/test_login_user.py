from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import delete, select, update
from sqlalchemy.engine import Connection

from app.infrastructure.database.models import SessionModel, UserModel
from app.infrastructure.database.session import SessionLocal


def _register(client: TestClient) -> dict[str, str]:
    unique = uuid4().hex[:10]
    payload = {
        'username': f'user{unique}',
        'full_name': 'Juan Perez',
        'email': f'{unique}@example.com',
        'password': f'password{unique}',
    }
    client.post('/api/v1/users', json=payload)
    return payload


def test_login_returns_200_with_user_data_and_token(client: TestClient) -> None:
    registered = _register(client)

    response = client.post(
        '/api/v1/login',
        json={'username': registered['username'], 'password': registered['password']},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data']['username'] == registered['username']
    assert body['data']['token']
    assert body['detail'] is None


def test_login_returns_400_when_password_is_incorrect(client: TestClient) -> None:
    registered = _register(client)

    response = client.post(
        '/api/v1/login',
        json={'username': registered['username'], 'password': 'wrongpassword1'},
    )

    assert response.status_code == 400
    body = response.json()
    assert body['success'] is False


def test_login_returns_400_when_username_does_not_exist(client: TestClient) -> None:
    response = client.post(
        '/api/v1/login',
        json={'username': 'doesnotexist1', 'password': 'whatever12'},
    )

    assert response.status_code == 400


def test_login_returns_400_when_user_is_not_active(
    client: TestClient, db_connection: Connection
) -> None:
    registered = _register(client)
    setup_session = SessionLocal(bind=db_connection)
    setup_session.execute(
        update(UserModel)
        .where(UserModel.username == registered['username'])
        .values(status='inactivo')
    )
    setup_session.flush()

    response = client.post(
        '/api/v1/login',
        json={'username': registered['username'], 'password': registered['password']},
    )

    assert response.status_code == 400
    body = response.json()
    assert (
        body['message']
        == 'Ocurrió un problema al iniciar sesión, llame a soporte técnico.'
    )


def test_login_returns_500_when_user_has_no_session(
    client: TestClient, db_connection: Connection
) -> None:
    registered = _register(client)
    setup_session = SessionLocal(bind=db_connection)
    user = setup_session.execute(
        select(UserModel).where(UserModel.username == registered['username'])
    ).scalar_one()
    setup_session.execute(delete(SessionModel).where(SessionModel.user_id == user.id))
    setup_session.flush()

    response = client.post(
        '/api/v1/login',
        json={'username': registered['username'], 'password': registered['password']},
    )

    assert response.status_code == 500
    body = response.json()
    assert body['success'] is False
    assert body['detail'] is None
