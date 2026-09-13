"""rename session invalidated_at to closed_at and add suspended status

Revision ID: e781e1fc04bd
Revises: 0178d1ff19d0
Create Date: 2026-09-13 21:36:31.484255

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e781e1fc04bd'
down_revision: Union[str, None] = '0178d1ff19d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('sessions', 'invalidated_at', new_column_name='closed_at')


def downgrade() -> None:
    op.alter_column('sessions', 'closed_at', new_column_name='invalidated_at')
