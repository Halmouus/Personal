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
    op.create_table('like_dislike',
        sa.Column('id', sa.String(length=36), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status_id', sa.String(length=36), sa.ForeignKey('status.id'), nullable=False),
        sa.Column('is_like', sa.Boolean, nullable=False)
    )

def downgrade():
    op.drop_table('like_dislike')

    # ### end Alembic commands ###
