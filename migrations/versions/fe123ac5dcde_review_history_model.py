"""review history model

Revision ID: fe123ac5dcde
Revises: c9c3c5f5968f
Create Date: 2023-10-30 17:50:07.114039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe123ac5dcde'
down_revision = 'c9c3c5f5968f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('data', sa.JSON(), nullable=True))
    op.drop_column('history', 'src_audio')
    op.drop_column('history', 'category')
    op.drop_column('history', 'img1')
    op.drop_column('history', 'poster')
    op.drop_column('history', 'title')
    op.drop_column('history', 'src_transcript')
    op.drop_column('history', 'detail')
    op.drop_column('history', 'status')
    op.drop_column('history', 'img2')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('img2', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('status', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('detail', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('src_transcript', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('poster', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('img1', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('history', sa.Column('src_audio', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('history', 'data')
    # ### end Alembic commands ###
