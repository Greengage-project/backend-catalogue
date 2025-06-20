"""disabled column added in softwareinterlinker

Revision ID: bdf345159032
Revises: 57af1c829618
Create Date: 2025-05-27 14:46:33.588618

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdf345159032'
down_revision = '57af1c829618'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('softwareinterlinker', sa.Column('disabled', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('softwareinterlinker', 'disabled')
    # ### end Alembic commands ###
