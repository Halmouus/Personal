"""Add tokens field to User model and create Token model

Revision ID: 234f5391bdbd
Revises: 91f930706253
Create Date: 2024-05-26 01:27:21.752524

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '234f5391bdbd'
down_revision = '91f930706253'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('token_value', sa.Integer(), nullable=False),
    sa.Column('issued_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tokens', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('tokens')

    op.drop_table('token')
    # ### end Alembic commands ###