from dataclasses import dataclass


@dataclass
class FieldConflict:
    field: str
    detail: str


class UserAlreadyExistsError(Exception):
    def __init__(self, conflicts: list[FieldConflict]) -> None:
        self.conflicts = conflicts
        super().__init__('User already exists')
