"""empty message

Revision ID: ddbb2d15d573
Revises: 5d5c439e5dc1
Create Date: 2023-09-15 20:06:16.468891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ddbb2d15d573'
down_revision = '5d5c439e5dc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('politician', schema=None) as batch_op:
        batch_op.add_column(sa.Column('district', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('politician', schema=None) as batch_op:
        batch_op.drop_column('district')

    # ### end Alembic commands ###