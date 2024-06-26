"""Update user_id and id to UUID in LikeDislike model

Revision ID: 9ac815c44950
Revises: 10cd4079a1d4
Create Date: 2024-05-26 22:47:40.644875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ac815c44950'
down_revision = '10cd4079a1d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('like_dislike', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('like_dislike', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###
