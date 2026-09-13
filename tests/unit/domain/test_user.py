from app.domain.entities.user import User, UserStatus


def test_register_normalizes_username_and_email_to_lowercase() -> None:
    user = User.register(
        username='JohnDoe123',
        full_name='John Doe',
        email='John.Doe@Example.com',
        password_hash='hashed-value',
    )

    assert user.username == 'johndoe123'
    assert user.email == 'john.doe@example.com'


def test_register_sets_initial_status_to_active() -> None:
    user = User.register(
        username='janedoe456',
        full_name='Jane Doe',
        email='jane@example.com',
        password_hash='hashed-value',
    )

    assert user.status == UserStatus.ACTIVE


def test_register_sets_created_and_updated_timestamps_equal() -> None:
    user = User.register(
        username='someuser1',
        full_name='Some User',
        email='some@example.com',
        password_hash='hashed-value',
    )

    assert user.created_at == user.updated_at
