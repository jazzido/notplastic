"""empty message

Revision ID: 40b99fc576ef
Revises: 634905e5787
Create Date: 2014-07-23 15:01:31.365509

"""

# revision identifiers, used by Alembic.
revision = '40b99fc576ef'
down_revision = '634905e5787'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('max_downloads', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'max_downloads')
    ### end Alembic commands ###
