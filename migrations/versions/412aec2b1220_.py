"""empty message

Revision ID: 412aec2b1220
Revises: 55646eba1476
Create Date: 2023-09-15 22:21:47.984519

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '412aec2b1220'
down_revision = '55646eba1476'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('loc_summary_association',
    sa.Column('loc_summary_id', sa.Integer(), nullable=True),
    sa.Column('loc_summary_code_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['loc_summary_code_id'], ['loc_summary_code.id'], ),
    sa.ForeignKeyConstraint(['loc_summary_id'], ['loc_summary.id'], )
    )
    op.drop_table('loc_summary_codes_association')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('loc_summary_codes_association',
    sa.Column('loc_summary_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('loc_summary_code_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['loc_summary_code_id'], ['loc_summary_code.id'], name='loc_summary_codes_association_loc_summary_code_id_fkey'),
    sa.ForeignKeyConstraint(['loc_summary_id'], ['loc_summary.id'], name='loc_summary_codes_association_loc_summary_id_fkey'),
    sa.PrimaryKeyConstraint('loc_summary_id', 'loc_summary_code_id', name='loc_summary_codes_association_pkey')
    )
    op.drop_table('loc_summary_association')
    # ### end Alembic commands ###
