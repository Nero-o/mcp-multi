"""empty message

Revision ID: 803260f773dc
Revises: fbafd78d5174
Create Date: 2025-04-10 17:20:55.829628

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '803260f773dc'
down_revision = 'fbafd78d5174'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota', schema=None) as batch_op:
        batch_op.add_column(sa.Column('metodo_assinatura', sa.String(length=50), server_default='aeco', nullable=False))
        batch_op.add_column(sa.Column('d4sign_document_uuid', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('fornecedor_nota', schema=None) as batch_op:
        batch_op.drop_column('d4sign_document_uuid')
        batch_op.drop_column('metodo_assinatura')

    # ### end Alembic commands ###
