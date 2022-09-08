from aiohttp.web_exceptions import HTTPConflict, HTTPNotFound, HTTPBadRequest
from aiohttp_apispec import querystring_schema, request_schema, response_schema, docs
from sqlalchemy.exc import IntegrityError

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema,
)
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class ThemeAddView(AuthRequiredMixin, View):
    @docs(tags=['quiz', 'theme'], sumary='add theme', description='Add theme in quiz')
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema)
    async def post(self):
        title = self.data["title"]
        try:
            theme = await self.store.quizzes.create_theme(title=title)
        except IntegrityError:
            raise HTTPConflict

        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(AuthRequiredMixin, View):
    @docs(tags=['quiz', 'theme'], sumary='get list themes',
          description='Get list all themes')
    @response_schema(ThemeListSchema)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data={
            'themes': [ThemeSchema().dump(theme) for theme in themes]
        })


class QuestionAddView(AuthRequiredMixin, View):
    @docs(tags=['quiz', 'question'], sumary='add question',
          description='Add question in quiz')
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema)
    async def post(self):
        data = self.data
        title, theme_id = data['title'], data['theme_id']
        answers = data['answers']
        answers = [Answer(title=answer['title'], is_correct=answer['is_correct']) for
                   answer in answers]

        if await self.request.app.store.quizzes.get_question_by_title(title):
            raise HTTPConflict

        if await self.request.app.store.quizzes.get_theme_by_id(theme_id) is None:
            raise HTTPNotFound

        if len(answers) == 1:
            raise HTTPBadRequest

        corrects = [answer.is_correct for answer in answers]
        is_all_correct = all(corrects)
        is_incorrect = [x for x in corrects if not x]

        if is_all_correct or len(is_incorrect) > 1:
            raise HTTPBadRequest

        question = await self.request.app.store.quizzes.create_question(
            title=title,
            theme_id=theme_id,
            answers=answers
        )

        response = QuestionSchema().dump(question)
        return json_response(data=response)


class QuestionListView(AuthRequiredMixin, View):
    @docs(tags=['quiz', 'question'], sumary='get list question',
          description='Get list question')
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema)
    async def get(self):
        questions_from_db = await self.request.app.store.quizzes.list_questions()
        return json_response(data={
            'questions': [
                QuestionSchema().dump(question) for question in questions_from_db
            ]
        })