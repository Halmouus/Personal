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
    op.create_table('like_dislike',
        sa.Column('id', sa.String(length=36), primary_key=True, default=uuid4),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('user.id')),
        sa.Column('status_id', sa.Integer, sa.ForeignKey('status.id')),
        sa.Column('is_like', sa.Boolean, nullable=False)
    )


def downgrade():
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_constraint('uq_user_pseudo', type_='unique')
        batch_op.alter_column('pseudo', existing_type=sa.String(length=80), nullable=True)

    # ### end Alembic commands ###
