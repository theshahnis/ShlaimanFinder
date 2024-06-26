"""added user notes and meeting_point db

Revision ID: b3489b0e8e79
Revises: bee0d823621a
Create Date: 2024-05-31 12:16:59.883205

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3489b0e8e79'
down_revision = 'bee0d823621a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('note', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('note')

    # ### end Alembic commands ###
