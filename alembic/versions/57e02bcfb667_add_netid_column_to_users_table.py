"""Add netid column to users table

Revision ID: 57e02bcfb667
Revises: fdb6c06ca1fb
Create Date: 2024-04-01 05:49:27.953288

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57e02bcfb667'
down_revision: Union[str, None] = 'fdb6c06ca1fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'netid',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint('netid_unique', 'users', type_='unique')
    op.drop_column('users', 'name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint('netid_unique', 'users', ['netid'])
    op.alter_column('users', 'netid',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
