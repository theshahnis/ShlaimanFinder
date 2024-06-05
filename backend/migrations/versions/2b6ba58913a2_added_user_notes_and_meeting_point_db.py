"""added user notes and meeting_point db

Revision ID: 2b6ba58913a2
Revises: fca44b8c0d1b
Create Date: 2024-05-31 13:50:31.339973

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b6ba58913a2'
down_revision = 'fca44b8c0d1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meeting_point', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meeting_point', schema=None) as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('duration')

    # ### end Alembic commands ###