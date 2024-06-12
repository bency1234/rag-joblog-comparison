"""add conversation id for storing conversations

Revision ID: 9cdef919a1fb
Revises: 14e48dcda7fc
Create Date: 2024-05-29 10:06:59.977761

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9cdef919a1fb"
down_revision = "14e48dcda7fc"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("uuid", sa.Text(), nullable=True),
        sa.Column("collection_name", sa.Text(), nullable=True),
        sa.Column("time_stamp", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("conversation")
    # ### end Alembic commands ###
