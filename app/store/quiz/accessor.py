import random
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    Answer,
    Question,
    Theme,
    ThemeModel,
    AnswerModel,
    QuestionModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        async with self.app.database.session.begin() as session:
            theme = ThemeModel(title=title)
            session.add(theme)
        return theme.to_dc()

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        async with self.app.database.session.begin() as session:
            query = select(ThemeModel).where(ThemeModel.title == title)
            res = await session.execute(query)
            theme = res.scalar()
            if theme:
                return theme.to_dc()
        return None

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        async with self.app.database.session.begin() as session:
            query = select(ThemeModel).where(ThemeModel.id == id_)
            res = await session.execute(query)
            theme = res.scalar()
            if theme:
                return theme.to_dc()
        return None

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session.begin() as session:
            query = select(ThemeModel)
            res = await session.execute(query)
            themes = res.scalars().all()
            themes = [theme.to_dc() for theme in themes]
        return themes

    async def create_answers(
        self, question_id: int, answers: list[Answer]
    ) -> list[Answer]:

        answers_models = [
            AnswerModel(
                title=answer.title,
                question_id=question_id,
            )
            for answer in answers
        ]

        async with self.app.database.session.begin() as session:
            session.add_all(answers_models)

        return [answer.to_dc() for answer in answers_models]

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        async with self.app.database.session.begin() as session:
            question = QuestionModel(
                title=title,
                theme_id=theme_id,
                answers=[AnswerModel(title=answer.title) for answer in answers],
            )
            session.add(question)
        return question.to_dc()

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        async with self.app.database.session.begin() as session:
            query = (
                select(QuestionModel)
                .where(QuestionModel.title == title)
                .options(joinedload(QuestionModel.answers))
            )
            question = await session.execute(query)
            question = question.scalar()
            if question:
                return question.to_dc()
        return None

    async def get_question_by_id(self, question_id: int) -> Optional[Question]:
        async with self.app.database.session.begin() as session:
            query = (
                select(QuestionModel)
                .where(QuestionModel.id == question_id)
                .options(joinedload(QuestionModel.answers))
            )
            res = await session.execute(query)
            question = res.scalar()
            if question:
                return question.to_dc()
        return None

    async def get_random_question(self) -> Question:
        async with self.app.database.session.begin() as session:
            query = select(QuestionModel)
            res = await session.execute(query)
            question_count = len(res.scalars().all())
        q_id = random.randint(1, question_count)
        question = await self.app.store.quizzes.get_question_by_id(q_id)
        if question is not None:
            return question
        else:
            await self.get_random_question()

    async def list_questions(self, theme_id: Optional[int] = None) -> list[Question]:
        async with self.app.database.session.begin() as session:
            if theme_id is not None:
                query = (
                    select(QuestionModel)
                    .where(QuestionModel.theme_id == theme_id)
                    .options(joinedload(QuestionModel.answers))
                )
            else:
                query = select(QuestionModel).options(joinedload(QuestionModel.answers))
            questions_from_db = await session.execute(query)
            questions_from_db = questions_from_db.scalars().unique()
            return [question.to_dc() for question in questions_from_db]

    async def get_answers_by_question_id(self, question_id: int) -> Optional[List[str]]:
        async with self.app.database.session.begin() as session:
            query = select(AnswerModel).where(AnswerModel.question_id == question_id)
            res = await session.execute(query)
            answers = res.scalars().all()
            if answers:
                return [answer.to_dc() for answer in answers]
        return None
