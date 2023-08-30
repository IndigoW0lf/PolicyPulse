"""Added new models

Revision ID: 77f97dfc5e31
Revises: 85921e097229
Create Date: 2023-08-30 13:35:54.332345

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77f97dfc5e31'
down_revision = '85921e097229'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('loc_summary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_code', sa.String(length=50), nullable=False),
    sa.Column('chamber', sa.String(length=50), nullable=True),
    sa.Column('action_description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('title_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('legislation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('action_type_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('loc_summary_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'loc_summary', ['loc_summary_id'], ['id'])
        batch_op.create_foreign_key(None, 'action_type', ['action_type_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('legislation', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('loc_summary_id')
        batch_op.drop_column('action_type_id')

    op.drop_table('title_type')
    op.drop_table('loc_summary')
    op.drop_table('action_type')
    # ### end Alembic commands ###