"""add patient_key_type to users

Revision ID: 007
Revises: 006
"""
from alembic import op
import sqlalchemy as sa

revision = "007_add_patient_key_type"
down_revision = "006_add_appointments"
branch_labels = None
depends_on = None

def upgrade():
    patient_key_type = sa.Enum('national_id', 'phone', 'email', name='patientkeytype')
    patient_key_type.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('patient_key_type', patient_key_type, server_default='national_id', nullable=False))

def downgrade():
    op.drop_column('users', 'patient_key_type')
    sa.Enum(name='patientkeytype').drop(op.get_bind(), checkfirst=True)
