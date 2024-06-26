"""Add TokenTransaction model

Revision ID: 7976a1ce9c6f
Revises: 234f5391bdbd
Create Date: 2024-05-26 01:58:48.433854

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7976a1ce9c6f'
down_revision = '234f5391bdbd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('token_transaction',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('sender_id', sa.String(length=36), nullable=False),
    sa.Column('recipient_id', sa.String(length=36), nullable=False),
    sa.Column('tokens', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['recipient_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('token_transaction')
    # ### end Alembic commands ###
