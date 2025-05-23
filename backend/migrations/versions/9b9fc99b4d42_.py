"""empty message

Revision ID: 9b9fc99b4d42
Revises: b52f337b5e5e
Create Date: 2025-03-21 15:10:10.823127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b9fc99b4d42'
down_revision = 'b52f337b5e5e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota_parcela', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_vencimento', sa.Date(), nullable=False))
        batch_op.add_column(sa.Column('data_pagamento', sa.Date(), nullable=True))
        batch_op.drop_column('data')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota_parcela', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data', sa.DATE(), nullable=False))
        batch_op.drop_column('data_pagamento')
        batch_op.drop_column('data_vencimento')

    # ### end Alembic commands ###
