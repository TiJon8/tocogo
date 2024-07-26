"""Updated Table

Revision ID: 577281ff0264
Revises: ac757baf4ae8
Create Date: 2024-07-03 11:24:12.844702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '577281ff0264'
down_revision: Union[str, None] = 'ac757baf4ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'last_name',
               existing_type=sa.VARCHAR(length=64),
               nullable=True)
    op.drop_column('users', 'is_active')
    # ### end Alembic commands ###
