"""auto migrations

Revision ID: a2c634a07f44
Revises: fb250e144a3a
Create Date: 2024-06-13 18:30:58.235340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2c634a07f44'
down_revision: Union[str, None] = 'fb250e144a3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('allocations_user_uuid_fkey', 'allocations', type_='foreignkey')
    op.drop_constraint('allocations_category_id_fkey', 'allocations', type_='foreignkey')
    op.create_foreign_key(None, 'allocations', 'categories', ['category_id'], ['category_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'allocations', 'users', ['user_uuid'], ['user_id'], ondelete='CASCADE')
    op.drop_constraint('bills_to_pay_allocation_id_fkey', 'bills_to_pay', type_='foreignkey')
    op.create_foreign_key(None, 'bills_to_pay', 'allocations', ['allocation_id'], ['alloc_id'], ondelete='CASCADE')
    op.drop_constraint('reference_books_allocation_id_fkey', 'reference_books', type_='foreignkey')
    op.create_foreign_key(None, 'reference_books', 'allocations', ['allocation_id'], ['alloc_id'], ondelete='CASCADE')
    op.drop_column('users', 'is_active')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'reference_books', type_='foreignkey')
    op.create_foreign_key('reference_books_allocation_id_fkey', 'reference_books', 'allocations', ['allocation_id'], ['alloc_id'])
    op.drop_constraint(None, 'bills_to_pay', type_='foreignkey')
    op.create_foreign_key('bills_to_pay_allocation_id_fkey', 'bills_to_pay', 'allocations', ['allocation_id'], ['alloc_id'])
    op.drop_constraint(None, 'allocations', type_='foreignkey')
    op.drop_constraint(None, 'allocations', type_='foreignkey')
    op.create_foreign_key('allocations_category_id_fkey', 'allocations', 'categories', ['category_id'], ['category_id'])
    op.create_foreign_key('allocations_user_uuid_fkey', 'allocations', 'users', ['user_uuid'], ['user_id'])
    # ### end Alembic commands ###