"""remove constraint time_to_notify

Revision ID: 40e1db45cf2e
Revises: 748f2f8d17bc
Create Date: 2024-11-10 21:58:38.510538

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "40e1db45cf2e"
down_revision: Union[str, None] = "748f2f8d17bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("check_time_to_notify_at_future", "notification", type_="check")


def downgrade() -> None:
    op.create_check_constraint(
        "check_time_to_notify_at_future", "notification", "time_to_notify > NOW()"
    )
