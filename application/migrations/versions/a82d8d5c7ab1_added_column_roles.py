"""added column roles

Revision ID: a82d8d5c7ab1
Revises: c75f38b7f0ab
Create Date: 2024-07-14 10:56:19.943113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a82d8d5c7ab1'
down_revision: Union[str, None] = 'c75f38b7f0ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('roles', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'roles')
    # ### end Alembic commands ###
