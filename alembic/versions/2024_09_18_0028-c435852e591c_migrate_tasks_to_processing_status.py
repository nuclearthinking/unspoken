"""migrate_tasks_to_processing_status

Revision ID: c435852e591c
Revises: 842029c9356f
Create Date: 2024-09-18 00:28:21.521541

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'c435852e591c'
down_revision: Union[str, None] = '842029c9356f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE task    
        SET status = 'processing' 
        WHERE status in ('conversion', 'diarization', 'transcribing')
    """)


def downgrade() -> None:
    op.execute("""
        UPDATE task
        SET status = 'failed'
        WHERE status = 'processing'
    """)
