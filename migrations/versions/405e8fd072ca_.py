"""empty message

Revision ID: 405e8fd072ca
Revises: 245ee6fe3086
Create Date: 2014-07-23 16:26:16.469048

"""

# revision identifiers, used by Alembic.
revision = '405e8fd072ca'
down_revision = '40b99fc576ef'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('extended_description', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'extended_description')
    ### end Alembic commands ###
