"""empty message

Revision ID: 27060d44ce56
Revises: 2b017edaa91f
Create Date: 2020-12-21 05:04:32.072466

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27060d44ce56'
down_revision = '2b017edaa91f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('avatar', sa.String(length=128), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'avatar')
    # ### end Alembic commands ###