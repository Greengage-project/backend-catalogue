"""themes_to_theme

Revision ID: 4f393c0c1381
Revises: d4006b515e70
Create Date: 2024-01-12 11:17:43.093694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f393c0c1381'
down_revision = 'd4006b515e70'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('interlinker', sa.Column('theme', sa.String(), nullable=True))
    op.drop_column('interlinker', 'themes')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('interlinker', sa.Column('themes', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('interlinker', 'theme')
    # ### end Alembic commands ###
