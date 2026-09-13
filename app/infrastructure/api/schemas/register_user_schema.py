from pydantic import BaseModel, EmailStr, Field

USERNAME_PATTERN = r'^[A-Za-z0-9]+$'
FULL_NAME_PATTERN = r'^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s]+$'
PHONE_PATTERN = r'^\+51 \d{9}$'
PASSWORD_PATTERN = r'^[A-Za-z0-9]+$'


class RegisterUserRequest(BaseModel):
    username: str = Field(min_length=9, max_length=50, pattern=USERNAME_PATTERN)
    full_name: str = Field(max_length=255, pattern=FULL_NAME_PATTERN)
    email: EmailStr = Field(max_length=255)
    phone: str | None = Field(
        default=None, min_length=13, max_length=13, pattern=PHONE_PATTERN
    )
    password: str = Field(min_length=9, max_length=100, pattern=PASSWORD_PATTERN)


class RegisterUserResponseData(BaseModel):
    username: str
    full_name: str
    status: str
    email: str
    phone: str | None
    token: str
