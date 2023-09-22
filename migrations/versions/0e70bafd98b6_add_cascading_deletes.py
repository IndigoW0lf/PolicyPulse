"""Add
 cascading deletes

Revision ID: 0e70bafd98b6
Revises: 2e1adc9f1ddb
Create Date: 2023-09-22 02:06:02.059099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e70bafd98b6'
down_revision = '2e1adc9f1ddb'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing foreign key constraints
    op.drop_constraint('bill_action_type_id_fkey', 'bill', type_='foreignkey')
    op.drop_constraint('bill_primary_subject_id_fkey',
                       'bill', type_='foreignkey')
    op.drop_constraint('bill_sponsor_id_fkey', 'bill', type_='foreignkey')

    # Add the foreign key constraints back with the ondelete='CASCADE' option
    op.create_foreign_key('bill_action_type_id_fkey', 'bill', 'action_type', [
                          'action_type_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('bill_primary_subject_id_fkey', 'bill', 'subject', [
                          'primary_subject_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('bill_sponsor_id_fkey', 'bill', 'politician', [
                          'sponsor_id'], ['id'], ondelete='CASCADE')


def downgrade():
    # Drop the foreign key constraints with the ondelete='CASCADE' option
    op.drop_constraint('bill_action_type_id_fkey', 'bill', type_='foreignkey')
    op.drop_constraint('bill_primary_subject_id_fkey',
                       'bill', type_='foreignkey')
    op.drop_constraint('bill_sponsor_id_fkey', 'bill', type_='foreignkey')

    # Add the foreign key constraints back without the ondelete='CASCADE' option
    op.create_foreign_key('bill_action_type_id_fkey',
                          'bill', 'action_type', ['action_type_id'], ['id'])
    op.create_foreign_key('bill_primary_subject_id_fkey',
                          'bill', 'subject', ['primary_subject_id'], ['id'])
    op.create_foreign_key('bill_sponsor_id_fkey', 'bill',
                          'politician', ['sponsor_id'], ['id'])
