"""migration

Revision ID: b03ea103cc8d
Revises: b2c542add394
Create Date: 2025-09-01 09:11:34.218523

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b03ea103cc8d'
down_revision = 'b2c542add394'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('telemetry', schema=None) as batch_op:
        # Only add columns if they do NOT exist
        pass  # Remove or comment out duplicate add_column lines

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('role')

    with op.batch_alter_table('telemetry', schema=None) as batch_op:
        # Only drop columns if you added them
        pass  # Remove or comment out duplicate drop_column lines