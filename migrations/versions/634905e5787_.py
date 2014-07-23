"""empty message

Revision ID: 634905e5787
Revises: 572453d72309
Create Date: 2014-07-23 14:47:19.224828

"""

# revision identifiers, used by Alembic.
revision = '634905e5787'
down_revision = '572453d72309'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('suggested_amount', sa.Numeric(precision=2), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('project', 'suggested_amount')
    ### end Alembic commands ###
