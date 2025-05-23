"""empty message

Revision ID: a0c1b2da6f50
Revises: bf34cffed246
Create Date: 2025-03-20 17:29:29.735586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a0c1b2da6f50'
down_revision = 'bf34cffed246'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota_parcela', schema=None) as batch_op:
        batch_op.create_foreign_key('FK_fornecedor_nota_parcela_status', 'status_nota_parcela', ['status_parcela_id'], ['id'])
        batch_op.create_foreign_key('FK_fornecedor_nota_parcela_status_admin', 'status_nota_parcela_admin', ['status_parcela_admin_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota_parcela', schema=None) as batch_op:
        batch_op.drop_constraint('FK_fornecedor_nota_parcela_status_admin', type_='foreignkey')
        batch_op.drop_constraint('FK_fornecedor_nota_parcela_status', type_='foreignkey')

    # ### end Alembic commands ###
