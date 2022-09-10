from typing import Optional

import marshmallow_dataclass
from marshmallow_dataclass import dataclass
from marshmallow import Schema, fields

from app.quiz.models import ThemeModel, QuestionModel, AnswerModel


@dataclass
class Theme:
    id: Optional[int]
    title: str

    def to_model(self):
        return ThemeModel(title=self.title)


@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list["Answer"]

    def to_model(self):
        answers = [answer.to_model() for answer in self.answers]
        return QuestionModel(title=self.title, theme_id=self.theme_id, answers=answers)


@dataclass
class Answer:
    title: str
    is_correct: bool

    def to_model(self):
        return AnswerModel(title=self.title)


ThemeSchema = marshmallow_dataclass.class_schema(Theme)
QuestionSchema = marshmallow_dataclass.class_schema(Question)
AnswerSchema = marshmallow_dataclass.class_schema(Answer)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int()


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)
