from uuid import UUID


class SessionNotFoundError(Exception):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f'No session found for user {user_id}')
