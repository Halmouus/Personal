"""Make pseudo nullable

Revision ID: 794547045f94
Revises: 2ff5a7c29bac
Create Date: 2024-05-26 09:34:42.684921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '794547045f94'
down_revision = '2ff5a7c29bac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=128),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)

    # ### end Alembic commands ###
