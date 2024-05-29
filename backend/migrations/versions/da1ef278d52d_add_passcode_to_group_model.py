"""Add passcode to group model

Revision ID: da1ef278d52d
Revises: f453da8e001e
Create Date: 2024-05-29 21:07:05.131850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da1ef278d52d'
down_revision = 'f453da8e001e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.add_column(sa.Column('passcode', sa.String(length=4), nullable=True))

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('passcode_attempts', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('passcode_attempts')

    with op.batch_alter_table('group', schema=None) as batch_op:
        batch_op.drop_column('passcode')

    # ### end Alembic commands ###
