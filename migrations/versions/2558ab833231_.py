"""empty message

Revision ID: 2558ab833231
Revises: 273741cce683
Create Date: 2023-09-01 21:13:43.221009

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2558ab833231'
down_revision = '273741cce683'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sponsor_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'politician', ['sponsor_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('sponsor_id')

    # ### end Alembic commands ###