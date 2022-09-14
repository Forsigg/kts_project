"""add rows to database

Revision ID: b59c8abd1248
Revises: 383fb05d37c8
Create Date: 2022-09-14 15:42:01.150847

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import table, column, Integer, String

revision = 'b59c8abd1248'
down_revision = '383fb05d37c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    themes_table = table('themes',
                         column('id', Integer),
                         column('title', String)
                         )
    op.bulk_insert(themes_table,
                   [
                       {'id': 1, 'title': 'Спорт'},
                       {'id': 2, 'title': 'Политика'},
                       {'id': 3, 'title': 'Жизнь'}
                   ])

    questions_table = table('questions',
                            column('id', Integer),
                            column('title', String),
                            column('theme_id', Integer)
                            )

    op.bulk_insert(questions_table,
                   [
                       {'id': 1, 'title': 'В какой игре не нужен мяч?', 'theme_id': 3},
                       {'id': 2, 'title': 'Вы каждый день встречаете этого человека. Кто он?', 'theme_id': 3},
                       {'id': 3, 'title': 'Где говорят правду? Ответ в именительном падеже', 'theme_id': 3}
                   ])

    answers_table = table('answers',
                          column('id', Integer),
                          column('title', String),
                          column('question_id', Integer)
                          )
    op.bulk_insert(answers_table,
                   [
                       {'id': 1, 'title': 'шахматы', 'question_id': 1},
                       {'id': 2, 'title': 'карты', 'question_id': 1},
                       {'id': 3, 'title': 'шашки', 'question_id': 1},
                       {'id': 4, 'title': 'домино', 'question_id': 1},
                       {'id': 5, 'title': 'хоккей', 'question_id': 1},
                       {'id': 6, 'title': 'прятки', 'question_id': 1},

                       {'id': 7, 'title': 'сосед', 'question_id': 2},
                       {'id': 8, 'title': 'муж', 'question_id': 2},
                       {'id': 9, 'title': 'жена', 'question_id': 2},
                       {'id': 10, 'title': 'начальник', 'question_id': 2},
                       {'id': 11, 'title': 'коллега', 'question_id': 2},
                       {'id': 12, 'title': 'родители', 'question_id': 2},

                       {'id': 13, 'title': 'суд', 'question_id': 3},
                       {'id': 14, 'title': 'нигде', 'question_id': 3},
                       {'id': 15, 'title': 'исповедь', 'question_id': 3},
                       {'id': 16, 'title': 'школа', 'question_id': 3},
                       {'id': 17, 'title': 'кухня', 'question_id': 3},
                       {'id': 18, 'title': 'загс', 'question_id': 3},
                   ])

    # ### end Alembic commands ###


def downgrade() -> None:
    #### commands auto generated by Alembic - please adjust! ###
    pass
    #### end Alembic commands ###
