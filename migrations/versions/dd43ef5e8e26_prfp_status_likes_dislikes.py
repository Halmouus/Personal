"""PrfP + Status + Likes/Dislikes

Revision ID: dd43ef5e8e26
Revises: 2d44ca34524b
Create Date: 2024-05-26 11:26:12.610655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd43ef5e8e26'
down_revision = '2d44ca34524b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('text', sa.String(length=500), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('likes', sa.Integer(), nullable=True),
    sa.Column('dislikes', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_picture', sa.String(length=150), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile_picture')

    op.drop_table('status')
    # ### end Alembic commands ###