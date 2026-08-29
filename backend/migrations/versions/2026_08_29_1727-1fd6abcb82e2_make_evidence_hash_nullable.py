"""make_evidence_hash_nullable

Revision ID: 1fd6abcb82e2
Revises: 'phase2_database_models'
Create Date: 2026-08-29 17:27:07.146019+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fd6abcb82e2'
down_revision: Union[str, None] = 'phase2_database_models'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make sha256_hash column nullable
    op.alter_column('evidence', 'sha256_hash', existing_type=sa.String(length=64), nullable=True)


def downgrade() -> None:
    # Revert sha256_hash column to non-nullable
    op.alter_column('evidence', 'sha256_hash', existing_type=sa.String(length=64), nullable=False)
