"""add full name to user

Revision ID: 2d9ad63d2485
Revises: f556deb8d0fa
Create Date: 2022-09-11 21:02:21.064996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d9ad63d2485'
down_revision = 'f556deb8d0fa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'full_name')
    op.create_table('questions',
    sa.Column('id', sa.BIGINT(), server_default=sa.text("nextval('questions_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('theme_id', sa.BIGINT(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], name='questions_theme_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='questions_pkey'),
    sa.UniqueConstraint('title', name='questions_title_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('themes',
    sa.Column('id', sa.BIGINT(), server_default=sa.text("nextval('themes_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='themes_pkey'),
    sa.UniqueConstraint('title', name='themes_title_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('answers',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name='answers_question_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='answers_pkey'),
    sa.UniqueConstraint('title', name='answers_title_key')
    )
    # ### end Alembic commands ###