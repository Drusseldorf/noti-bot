"""delete not null constraits for user

Revision ID: df84c8a54911
Revises: 6955fb947fef
Create Date: 2024-11-11 18:28:27.794013

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "df84c8a54911"
down_revision: Union[str, None] = "6955fb947fef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "user", "minutes_before_noti", existing_type=sa.Integer(), nullable=True
    )
    op.alter_column("user", "timezone", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column(
        "user", "minutes_before_noti", existing_type=sa.Integer(), nullable=False
    )
    op.alter_column("user", "timezone", existing_type=sa.Integer(), nullable=False)
