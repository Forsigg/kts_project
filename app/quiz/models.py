from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.quiz.schemes import Theme, Question, Answer
from app.store.database.sqlalchemy_base import db


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)

    def to_dc(self) -> Theme:
        return Theme(id=self.id, title=self.title)


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    theme_id = Column(ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    answers = relationship("AnswerModel")

    def to_dc(self) -> Question:
        return Question(
            id=self.id,
            title=self.title,
            theme_id=self.theme_id,
            answers=[
                Answer(
                    title=answer.title,
                )
                for answer in self.answers
            ],
        )


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    question_id = Column(
        Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False
    )

    def to_dc(self) -> Answer:
        return Answer(
            title=self.title,
        )
