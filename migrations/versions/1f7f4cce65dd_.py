"""empty message

Revision ID: 1f7f4cce65dd
Revises: b3db472dc05b
Create Date: 2023-09-08 00:58:12.580042

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1f7f4cce65dd'
down_revision = 'b3db472dc05b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('action_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('description')
    )
    op.create_table('committee',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('chamber', sa.String(length=50), nullable=False),
    sa.Column('committee_code', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('committee_code'),
    sa.UniqueConstraint('name')
    )
    op.create_table('politician',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=True),
    sa.Column('party', sa.String(length=50), nullable=True),
    sa.Column('role', sa.String(length=100), nullable=True),
    sa.Column('profile_link', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subject',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('title_type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('bill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('date_introduced', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=100), nullable=True),
    sa.Column('bill_number', sa.String(length=50), nullable=False),
    sa.Column('sponsor_name', sa.String(length=200), nullable=False),
    sa.Column('committee', sa.String(length=200), nullable=True),
    sa.Column('voting_record', sa.Text(), nullable=True),
    sa.Column('full_bill_link', sa.String(length=500), nullable=True),
    sa.Column('tags', sa.String(length=300), nullable=True),
    sa.Column('last_action_date', sa.Date(), nullable=True),
    sa.Column('last_action_description', sa.Text(), nullable=True),
    sa.Column('congress', sa.String(length=50), nullable=True),
    sa.Column('bill_type', sa.String(length=50), nullable=True),
    sa.Column('update_date', sa.Date(), nullable=True),
    sa.Column('xml_content', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    sa.Column('action_type_id', sa.Integer(), nullable=True),
    sa.Column('sponsor_id', sa.Integer(), nullable=False),
    sa.Column('title_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['action_type_id'], ['action_type.id'], ),
    sa.ForeignKeyConstraint(['sponsor_id'], ['politician.id'], ),
    sa.ForeignKeyConstraint(['title_type_id'], ['title_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bill_bill_number'), ['bill_number'], unique=True)

    op.create_table('action',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('action_date', sa.Date(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('chamber', sa.Enum('House', 'Senate', name='chamber_types'), nullable=True),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('action_type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['action_type_id'], ['action_type.id'], ),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_action_action_type_id'), ['action_type_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_action_bill_id'), ['bill_id'], unique=False)

    op.create_table('amendment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amendment_number', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date_proposed', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('PROPOSED', 'ACCEPTED', 'REJECTED', name='amendmentstatusenum'), nullable=True),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('amendment', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_amendment_bill_id'), ['bill_id'], unique=False)

    op.create_table('bill_committee',
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('committee_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.ForeignKeyConstraint(['committee_id'], ['committee.id'], ),
    sa.PrimaryKeyConstraint('bill_id', 'committee_id')
    )
    op.create_table('bill_full_text',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('meta_data', sa.JSON(), nullable=True),
    sa.Column('actions', sa.JSON(), nullable=True),
    sa.Column('sections', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('bill_full_text', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bill_full_text_bill_id'), ['bill_id'], unique=False)

    op.create_table('bill_subject',
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
    sa.PrimaryKeyConstraint('bill_id', 'subject_id')
    )
    with op.batch_alter_table('bill_subject', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_bill_subject_bill_id'), ['bill_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_bill_subject_subject_id'), ['subject_id'], unique=False)

    op.create_table('co_sponsor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('politician_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.ForeignKeyConstraint(['politician_id'], ['politician.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('co_sponsor', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_co_sponsor_bill_id'), ['bill_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_co_sponsor_politician_id'), ['politician_id'], unique=False)

    op.create_table('loc_summary',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('version_code', sa.String(length=50), nullable=False),
    sa.Column('chamber', sa.String(length=50), nullable=True),
    sa.Column('action_description', sa.String(length=200), nullable=False),
    sa.Column('summary_text', sa.Text(), nullable=True),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('loc_summary', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_loc_summary_bill_id'), ['bill_id'], unique=False)

    op.create_table('related_bill',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bill_id', sa.Integer(), nullable=False),
    sa.Column('related_bill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], ),
    sa.ForeignKeyConstraint(['related_bill_id'], ['bill.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('related_bill', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_related_bill_bill_id'), ['bill_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_related_bill_related_bill_id'), ['related_bill_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('related_bill', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_related_bill_related_bill_id'))
        batch_op.drop_index(batch_op.f('ix_related_bill_bill_id'))

    op.drop_table('related_bill')
    with op.batch_alter_table('loc_summary', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_loc_summary_bill_id'))

    op.drop_table('loc_summary')
    with op.batch_alter_table('co_sponsor', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_co_sponsor_politician_id'))
        batch_op.drop_index(batch_op.f('ix_co_sponsor_bill_id'))

    op.drop_table('co_sponsor')
    with op.batch_alter_table('bill_subject', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bill_subject_subject_id'))
        batch_op.drop_index(batch_op.f('ix_bill_subject_bill_id'))

    op.drop_table('bill_subject')
    with op.batch_alter_table('bill_full_text', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bill_full_text_bill_id'))

    op.drop_table('bill_full_text')
    op.drop_table('bill_committee')
    with op.batch_alter_table('amendment', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_amendment_bill_id'))

    op.drop_table('amendment')
    with op.batch_alter_table('action', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_action_bill_id'))
        batch_op.drop_index(batch_op.f('ix_action_action_type_id'))

    op.drop_table('action')
    with op.batch_alter_table('bill', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_bill_bill_number'))

    op.drop_table('bill')
    op.drop_table('title_type')
    op.drop_table('subject')
    op.drop_table('politician')
    op.drop_table('committee')
    op.drop_table('action_type')
    # ### end Alembic commands ###
