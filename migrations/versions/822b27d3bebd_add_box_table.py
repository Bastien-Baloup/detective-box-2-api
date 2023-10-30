"""add box table

Revision ID: 822b27d3bebd
Revises: b52f0ae18f59
Create Date: 2023-10-22 20:44:49.641700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '822b27d3bebd'
down_revision = 'b52f0ae18f59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('box',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_box_id'), 'box', ['id'], unique=False)
    op.create_table('user_box',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('box_id', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('open', 'closed', 'done', name='boxstatus'), nullable=True),
    sa.ForeignKeyConstraint(['box_id'], ['box.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'box_id')
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_box')
    op.drop_index(op.f('ix_box_id'), table_name='box')
    op.drop_table('box')
    sa.Enum('open', 'closed', 'done', name='boxstatus').drop(op.get_bind())
    # ### end Alembic commands ###
