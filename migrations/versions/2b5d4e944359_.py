"""empty message

Revision ID: 2b5d4e944359
Revises: 1f9efabc486
Create Date: 2014-07-22 18:08:00.891120

"""

# revision identifiers, used by Alembic.
revision = '2b5d4e944359'
down_revision = '1f9efabc486'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('collection_status', sa.Column('created_at', sa.DateTime(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('collection_status', 'created_at')
    ### end Alembic commands ###
