"""review character model

Revision ID: 19aca860e66f
Revises: 06847469412e
Create Date: 2023-10-30 21:47:59.442038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19aca860e66f'
down_revision = '06847469412e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('help', sa.Column('ref', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('help', 'ref')
    # ### end Alembic commands ###
