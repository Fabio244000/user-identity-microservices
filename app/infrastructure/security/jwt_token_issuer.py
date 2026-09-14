from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from jose import JWTError, jwt

from app.domain.ports.output.token_issuer_port import (
    DecodedToken,
    IssuedToken,
    TokenIssuerPort,
)
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

    def decode(self, token: str) -> DecodedToken | None:
        try:
            payload = jwt.decode(
                token,
                self._settings.secret_key,
                algorithms=[JWT_ALGORITHM],
                options={'verify_exp': False},
            )
        except JWTError:
            return None
        jti = payload.get('jti')
        exp = payload.get('exp')
        if jti is None or exp is None:
            return None
        is_expired = datetime.now(UTC).timestamp() > exp
        return DecodedToken(jti=jti, is_expired=is_expired)
