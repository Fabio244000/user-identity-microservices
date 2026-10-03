from app.migrate_handler import _run_migrations


def test_run_migrations_is_idempotent_when_already_applied() -> None:
    _run_migrations()
    _run_migrations()
