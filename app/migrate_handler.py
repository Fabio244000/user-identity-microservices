import json
import urllib.request
from pathlib import Path

from alembic.command import upgrade
from alembic.config import Config

ALEMBIC_INI_PATH = Path(__file__).resolve().parent.parent / 'alembic.ini'


def handler(event: dict[str, object], context: object) -> dict[str, str]:
    try:
        if event.get('RequestType') != 'Delete':
            _run_migrations()
        _send_response(event, 'SUCCESS')
    except Exception as error:
        _send_response(event, 'FAILED', reason=str(error))
        raise
    return {'status': 'ok'}


def _run_migrations() -> None:
    config = Config(str(ALEMBIC_INI_PATH))
    upgrade(config, 'head')


def _send_response(
    event: dict[str, object], status: str, reason: str | None = None
) -> None:
    body = json.dumps(
        {
            'Status': status,
            'Reason': reason or 'See CloudWatch Logs for details.',
            'PhysicalResourceId': event.get('LogicalResourceId', 'MigrationTrigger'),
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
        }
    ).encode('utf-8')
    request = urllib.request.Request(
        url=str(event['ResponseURL']),
        data=body,
        method='PUT',
        headers={'Content-Type': ''},
    )
    urllib.request.urlopen(request)
