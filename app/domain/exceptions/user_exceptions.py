from dataclasses import dataclass


@dataclass
class FieldConflict:
    field: str
    detail: str


class UserAlreadyExistsError(Exception):
    def __init__(self, conflicts: list[FieldConflict]) -> None:
        self.conflicts = conflicts
        super().__init__('User already exists')


class InvalidCredentialsError(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid username or password')


class LoginNotAllowedError(Exception):
    def __init__(self) -> None:
        super().__init__('Login is not allowed for this account')
