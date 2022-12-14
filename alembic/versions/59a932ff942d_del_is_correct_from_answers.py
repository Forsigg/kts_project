"""del is_correct from answers

Revision ID: 59a932ff942d
Revises: b471319d4627
Create Date: 2022-09-08 21:32:24.166644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59a932ff942d'
down_revision = 'b471319d4627'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('answers', 'is_correct')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('answers', sa.Column('is_correct', sa.BOOLEAN(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
