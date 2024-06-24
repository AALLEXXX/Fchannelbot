"""empty message

Revision ID: 317f96d23c38
Revises: 
Create Date: 2024-06-24 17:00:59.415748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '317f96d23c38'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.Column('reg_date', sa.DateTime(), nullable=True),
    sa.Column('tg_username', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('chat_id'),
    sa.UniqueConstraint('tg_username')
    )
    op.create_table('users_subs',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date_from', sa.DateTime(), nullable=False),
    sa.Column('date_to', sa.DateTime(), nullable=False),
    sa.Column('link', sa.String(), nullable=True),
    sa.Column('tg_username', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['tg_username'], ['users.tg_username'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('link'),
    sa.UniqueConstraint('tg_username')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users_subs')
    op.drop_table('users')
    # ### end Alembic commands ###
