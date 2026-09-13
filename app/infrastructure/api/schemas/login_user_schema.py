from pydantic import BaseModel, Field

from app.infrastructure.api.schemas.patterns import PASSWORD_PATTERN, USERNAME_PATTERN


class LoginUserRequest(BaseModel):
    username: str = Field(min_length=9, max_length=50, pattern=USERNAME_PATTERN)
    password: str = Field(min_length=9, max_length=100, pattern=PASSWORD_PATTERN)


class LoginUserResponseData(BaseModel):
    username: str
    full_name: str
    status: str
    email: str
    phone: str | None
    token: str
