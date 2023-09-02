"""Added title_type_id to Bill

Revision ID: b8d7864a171e
Revises: 7ed7d497004a
Create Date: 2023-09-01 23:10:17.337302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8d7864a171e'
down_revision = '7ed7d497004a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title_type_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'title_type', ['title_type_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('title_type_id')

    # ### end Alembic commands ###
