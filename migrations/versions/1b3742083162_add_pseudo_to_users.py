"""Add pseudo to users

Revision ID: 1b3742083162
Revises: 7976a1ce9c6f
Create Date: 2024-05-26 09:17:39.699437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b3742083162'
down_revision = '7976a1ce9c6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pseudo', sa.String(length=150), nullable=False))
        batch_op.create_unique_constraint('uq_user_pseudo', ['pseudo'])


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('pseudo')

    # ### end Alembic commands ###
