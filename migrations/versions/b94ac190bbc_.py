"""empty message

Revision ID: b94ac190bbc
Revises: 405e8fd072ca
Create Date: 2014-07-24 14:55:12.145510

"""

# revision identifiers, used by Alembic.
revision = 'b94ac190bbc'
down_revision = '405e8fd072ca'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('background_image_url', sa.String(length=512), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'background_image_url')
    ### end Alembic commands ###
