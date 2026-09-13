from app.domain.exceptions.user_exceptions import FieldConflict, UserAlreadyExistsError


def test_carries_the_list_of_field_conflicts() -> None:
    conflicts = [FieldConflict(field='username', detail='some detail')]

    error = UserAlreadyExistsError(conflicts)

    assert error.conflicts == conflicts
