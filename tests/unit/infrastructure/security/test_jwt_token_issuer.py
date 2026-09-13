from uuid import uuid4

from jose import jwt

from app.infrastructure.security.jwt_token_issuer import JWT_ALGORITHM, JwtTokenIssuer
from config.settings import Settings


def _build_settings(session_duration_minutes: int = 30) -> Settings:
    return Settings(
        postgres_user='user',
        postgres_password='password',
        postgres_db='db',
        database_url='postgresql+psycopg://user:password@localhost:5432/db',
        secret_key='test-secret-key',
        session_duration_minutes=session_duration_minutes,
    )


def test_issue_returns_a_token_carrying_the_user_id_and_matching_jti() -> None:
    issuer = JwtTokenIssuer(_build_settings())
    user_id = uuid4()

    issued = issuer.issue(user_id)

    payload = jwt.decode(issued.token, 'test-secret-key', algorithms=[JWT_ALGORITHM])
    assert payload['sub'] == str(user_id)
    assert payload['jti'] == issued.jti


def test_issue_sets_expiration_based_on_session_duration_minutes() -> None:
    settings = _build_settings(session_duration_minutes=1)
    issuer = JwtTokenIssuer(settings)

    issued = issuer.issue(uuid4())

    payload = jwt.decode(issued.token, settings.secret_key, algorithms=[JWT_ALGORITHM])
    assert payload['exp'] - payload['iat'] == 60
