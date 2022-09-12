from typing import Optional, List, TYPE_CHECKING, Tuple
from sqlalchemy.exc import IntegrityError

from app.game.models import User, Score, Game
from app.quiz.schemes import Question, Answer
from app.store.vk_api.dataclasses import Message

if TYPE_CHECKING:
    from app.web.app import Application


class GameManager:
    STATES = ('CREATED', 'WAITING', 'CHECKING', 'DONE')

    def __init__(self, app: "Application") -> None:
        self.game: Optional[Game] = None
        self.app = app
        self.current_question: Optional[Question] = None
        self.state: Optional[str] = None
        self.is_active: bool = True
        self.chat_id: Optional[int] = None
        self.scores: Optional[List[Score]] = None
        self.users: Optional[List[User]] = None

    async def main(self, chat_id: int):
        # TODO: доделать основную функцию
        await self.start_game(chat_id)

        while len(self.users) > 1:
            await self.send_question()

    async def is_correct_answer(self, answer: Answer) -> bool:
        answers = self.current_question.answers
        for answer_from_question in answers:
            if answer.title == answer_from_question.title:
                return True
        return False

    async def is_game_over(self, chat_id: int) -> bool:
        if len(self.users) == 1:
            return True
        return False

    async def start_game(self, chat_id: int) -> None:
        self.state = 'CREATED'
        self.chat_id = chat_id
        self.users = await self.app.store.vk_api.get_conversation_members(peer_id=chat_id)
        self.game = await self.app.store.games.create_game()
        for user in self.users:
            try:
                await self.app.store.games.create_user(user.id, user.full_name)
            except IntegrityError:
                pass
        self.scores = await self.app.store.games.create_start_score(
            game_id=self.game.id,
            users_id=[user.id for user in self.users]
        )
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Добрый день! Начинаем игру 100 к 1. Игра № {self.game.id}, участники: '
                 f'{",".join([user.full_name for user in self.users])}'
        ))

    async def send_question(self) -> None:
        question = self.app.store.quizzes.get_random_question()
        self.current_question = question
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"{question.title}"
        ))
        self.state = 'WAITING'

    async def user_kick(self, user_id: int) -> None:
        for user in self.users:
            if user.id == user_id:
                lose_user = user
        self.users.remove(lose_user)

        for score in self.scores:
            if score.player.id == user_id:
                score.total = 0
                await self.app.store.games.update_score_to_zero_point(score.id)

        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {lose_user.full_name} выбывает!"
        ))

    async def is_user_kicked(self, user_id: int) -> bool:
        for user in self.users:
            if user.id == user_id:
                return False
        return True

    async def add_point(self, user_id: int) -> None:
        old_score = list(filter(lambda x: x.player.id == user_id, self.scores))[0]
        new_score = await self.app.store.games.add_one_point_to_score(score_id=old_score.id)
        self.scores.remove(old_score)
        self.scores.append(new_score)
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {new_score.player.full_name} получает 1 очко!"
        ))

    async def end_game(self, chat_id: int):
        self.state = 'DONE'
        results = ''
        for score in self.scores:
            results += f'{score.player.full_name}: {score.total} \n'

        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=results
        ))

        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Игра закончена, всем до свидания!'
        ))

        await self.app.store.games.change_game_not_active(self.game.id)

        self.game = None
        self.users = None
        self.scores = None
        self.current_question = None
        self.is_active = False



