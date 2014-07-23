"""empty message

Revision ID: 55fce4de1348
Revises: 234152e69e15
Create Date: 2014-07-21 16:36:29.091171

"""

# revision identifiers, used by Alembic.
revision = '55fce4de1348'
down_revision = '234152e69e15'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('mercado_pago_payment_preference', sa.Column('definition', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('mercado_pago_payment_preference', 'definition')
    ### end Alembic commands ###