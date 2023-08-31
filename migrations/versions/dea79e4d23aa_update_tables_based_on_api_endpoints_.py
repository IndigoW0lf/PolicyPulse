"""Update tables based on API endpoints and routes

Revision ID: dea79e4d23aa
Revises: 77f97dfc5e31
Create Date: 2023-08-30 22:32:03.809375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dea79e4d23aa'
down_revision = '77f97dfc5e31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Bill', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sponsor_name', sa.String(length=200), nullable=False))
        batch_op.add_column(sa.Column('congress', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('bill_type', sa.String(length=50), nullable=True))

    with op.batch_alter_table('loc_summary', schema=None) as batch_op:
        batch_op.add_column(sa.Column('summary_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('Bill_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Bill', ['Bill_id'], ['id'])

    with op.batch_alter_table('politician', schema=None) as batch_op:
        batch_op.drop_constraint('politician_sponsored_bill_id_fkey', type_='foreignkey')
        batch_op.drop_column('sponsored_bill_id')

    with op.batch_alter_table('title_type', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['code'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('title_type', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('politician', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sponsored_bill_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('politician_sponsored_bill_id_fkey', 'Bill', ['sponsored_bill_id'], ['id'])

    with op.batch_alter_table('loc_summary', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('Bill_id')
        batch_op.drop_column('summary_text')

    with op.batch_alter_table('Bill', schema=None) as batch_op:
        batch_op.drop_column('bill_type')
        batch_op.drop_column('congress')
        batch_op.drop_column('sponsor_name')

    # ### end Alembic commands ###