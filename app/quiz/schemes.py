from typing import Optional

from marshmallow_dataclass import dataclass
from marshmallow import Schema, fields


@dataclass
class Theme:
    id: Optional[int]
    title: str


@dataclass
class Answer:
    title: str



@dataclass
class Question:
    id: Optional[int]
    title: str
    theme_id: int
    answers: list[Answer]


ThemeSchema = Theme.Schema()
AnswerSchema = Answer.Schema()
QuestionSchema = Question.Schema()


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int()


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)
