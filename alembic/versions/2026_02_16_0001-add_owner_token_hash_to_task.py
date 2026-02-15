"""Add owner_token_hash to task.

Revision ID: a1b2c3d4e5f6
Revises: 989ae533399c
Create Date: 2026-02-16 00:01:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '989ae533399c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('task', sa.Column('owner_token_hash', sa.String(64), nullable=True))


def downgrade() -> None:
    op.drop_column('task', 'owner_token_hash')
