from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jose import jwt

from app.domain.ports.output.token_issuer_port import IssuedToken, TokenIssuerPort
from config.settings import Settings

JWT_ALGORITHM = 'HS256'


class JwtTokenIssuer(TokenIssuerPort):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def issue(self, user_id: UUID) -> IssuedToken:
        jti = str(uuid4())
        issued_at = datetime.now(UTC)
        expires_at = issued_at + timedelta(
            minutes=self._settings.session_duration_minutes
        )
        payload = {
            'sub': str(user_id),
            'jti': jti,
            'iat': issued_at,
            'exp': expires_at,
        }
        token = jwt.encode(payload, self._settings.secret_key, algorithm=JWT_ALGORITHM)
        return IssuedToken(token=token, jti=jti)
