"""auto migrations

Revision ID: 6e24c19a809e
Revises: 4a8c5e1f9fb5
Create Date: 2024-06-16 13:08:21.095375

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e24c19a809e'
down_revision: Union[str, None] = '4a8c5e1f9fb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
