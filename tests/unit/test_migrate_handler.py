import json
from unittest.mock import patch

import pytest
from sqlalchemy.exc import OperationalError

from app.migrate_handler import handler


def _build_event(request_type: str = 'Create') -> dict[str, object]:
    return {
        'RequestType': request_type,
        'ResponseURL': 'https://example.com/cfn-response',
        'StackId': 'arn:aws:cloudformation:us-east-1:123456789012:stack/test/abc',
        'RequestId': 'request-123',
        'LogicalResourceId': 'MigrationTrigger',
    }


@patch('urllib.request.urlopen')
@patch('app.migrate_handler.upgrade')
def test_handler_runs_migration_and_sends_success_on_create(
    mock_upgrade: object, mock_urlopen: object
) -> None:
    event = _build_event('Create')

    result = handler(event, None)

    mock_upgrade.assert_called_once()
    assert mock_urlopen.called
    sent_request = mock_urlopen.call_args[0][0]
    assert sent_request.get_method() == 'PUT'
    sent_body = json.loads(sent_request.data)
    assert sent_body['Status'] == 'SUCCESS'
    assert result == {'status': 'ok'}


@patch('urllib.request.urlopen')
@patch('app.migrate_handler.upgrade')
def test_handler_skips_migration_on_delete(
    mock_upgrade: object, mock_urlopen: object
) -> None:
    event = _build_event('Delete')

    handler(event, None)

    mock_upgrade.assert_not_called()
    assert mock_urlopen.called


@patch('urllib.request.urlopen')
@patch('app.migrate_handler.upgrade', side_effect=RuntimeError('boom'))
def test_handler_sends_failure_and_reraises_when_migration_fails(
    mock_upgrade: object, mock_urlopen: object
) -> None:
    event = _build_event('Create')

    with pytest.raises(RuntimeError):
        handler(event, None)

    assert mock_urlopen.called
    sent_request = mock_urlopen.call_args[0][0]
    sent_body = json.loads(sent_request.data)
    assert sent_body['Status'] == 'FAILED'
    assert 'boom' in sent_body['Reason']


@patch('urllib.request.urlopen')
@patch(
    'app.migrate_handler.upgrade',
    side_effect=OperationalError('SELECT 1', {}, Exception('connection refused')),
)
def test_handler_sends_failure_and_reraises_when_database_is_unreachable(
    mock_upgrade: object, mock_urlopen: object
) -> None:
    event = _build_event('Create')

    with pytest.raises(OperationalError):
        handler(event, None)

    assert mock_urlopen.called
    sent_request = mock_urlopen.call_args[0][0]
    sent_body = json.loads(sent_request.data)
    assert sent_body['Status'] == 'FAILED'
    assert 'connection refused' in sent_body['Reason']


@patch('urllib.request.urlopen')
@patch('app.migrate_handler.upgrade')
def test_handler_runs_migration_on_update_request_type(
    mock_upgrade: object, mock_urlopen: object
) -> None:
    event = _build_event('Update')

    handler(event, None)

    mock_upgrade.assert_called_once()
    assert mock_urlopen.called
    sent_request = mock_urlopen.call_args[0][0]
    sent_body = json.loads(sent_request.data)
    assert sent_body['Status'] == 'SUCCESS'
