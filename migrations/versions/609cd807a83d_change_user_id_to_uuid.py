"""Change User ID to UUID

Revision ID: 609cd807a83d
Revises: b1a92dbaf887
Create Date: 2024-05-20 23:17:21.165014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '609cd807a83d'
down_revision = 'b1a92dbaf887'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the foreign key constraint first
    op.drop_constraint('login_session_ibfk_1', 'login_session', type_='foreignkey')

    with op.batch_alter_table('login_session', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=False)

    # Re-create the foreign key constraint
    op.create_foreign_key('login_session_ibfk_1', 'login_session', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop the foreign key constraint first
    op.drop_constraint('login_session_ibfk_1', 'login_session', type_='foreignkey')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('login_session', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # Re-create the foreign key constraint
    op.create_foreign_key('login_session_ibfk_1', 'login_session', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###
