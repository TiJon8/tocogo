"""Added Composite Table

Revision ID: cb939bbc46e0
Revises: 533b29571ba5
Create Date: 2024-07-24 02:29:00.390389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import db


# revision identifiers, used by Alembic.
revision: str = 'cb939bbc46e0'
down_revision: Union[str, None] = '533b29571ba5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('composites',
    sa.Column('composite_id', db.schemas.GUID(), nullable=False),
    sa.Column('composite_name', sa.String(), nullable=False),
    sa.Column('composite_description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('composite_status', sa.Enum('active', 'done', name='activeobject'), nullable=False),
    sa.Column('user_id', db.schemas.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name=op.f('fk_composites_user_id_users')),
    sa.PrimaryKeyConstraint('composite_id', name=op.f('pk_composites'))
    )
    op.create_table('tasks',
    sa.Column('task_id', db.schemas.GUID(), nullable=False),
    sa.Column('task_description', sa.Text(), nullable=False),
    sa.Column('task_level', sa.Enum('free', 'optimal', 'urgent', name='tasklevel'), nullable=False),
    sa.Column('composite_id', db.schemas.GUID(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('task_status', sa.Enum('active', 'done', name='activeobject'), nullable=False),
    sa.Column('closed_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['composite_id'], ['composites.composite_id'], name=op.f('fk_tasks_composite_id_composites')),
    sa.PrimaryKeyConstraint('task_id', name=op.f('pk_tasks'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tasks')
    op.drop_table('composites')
    # ### end Alembic commands ###
