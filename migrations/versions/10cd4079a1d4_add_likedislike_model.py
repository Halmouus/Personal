"""Add LikeDislike model

Revision ID: 10cd4079a1d4
Revises: dd43ef5e8e26
Create Date: 2024-05-26 22:40:04.472260

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '10cd4079a1d4'
down_revision = 'dd43ef5e8e26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('like_dislike',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('status_id', sa.String(length=36), nullable=False),
    sa.Column('is_like', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['status_id'], ['status.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###



def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('like_dislike')
    # ### end Alembic commands ###
