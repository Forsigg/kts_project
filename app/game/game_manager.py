from typing import Optional, List, TYPE_CHECKING, Tuple
from sqlalchemy.exc import IntegrityError

from app.game.models import User, Score, Game
from app.quiz.schemes import Question, Answer
from app.store.vk_api.dataclasses import Message

if TYPE_CHECKING:
    from app.web.app import Application


class GameManager:
    STATES = {
        1: "started",
        2: "question",
        3: "waiting",
        4: "checking",
        5: "done"
        }

    def __init__(self, app: "Application") -> None:
        self.game: Optional[Game] = None
        self.app = app
        self.question: Optional[Question] = None
        self.state: Optional[str] = None
        self.chat_id: Optional[int] = None
        self.scores: Optional[List[Score]] = None
        self.users: Optional[List[User]] = None
        self.used_answers: Optional[List[str]] = None

    async def main(self, chat_id: int):
        # TODO: доделать основную функцию
        await self.start_game(chat_id)

        while len(self.users) > 1:
            await self.send_question()

    async def start_game(self, chat_id: int) -> None:
        self.state = self.STATES[1]
        self.chat_id = chat_id
        self.users = await self.app.store.vk_api.get_conversation_members(peer_id=chat_id)
        self.game = await self.app.store.games.create_game()
        self.question = await self.app.store.quizzes.get_question_by_id(self.game.question_id)
        self.used_answers = []
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
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=2)
        self.state = self.STATES[2]

    async def send_question(self) -> None:
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"{self.question.title}"
        ))
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=3)
        self.state = self.STATES[3]

    async def user_kick(self, user_id: int) -> None:
        for score in self.scores:
            if score.user_id == user_id:
                score.total = -1
                await self.app.store.games.update_score_to_minus_one_point(score.id)

        lose_user = list(filter(lambda x: x.id == user_id, self.users))[0]
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {lose_user.full_name} выбывает!"
        ))

    async def is_user_kicked(self, user_id: int) -> bool:
        for score in self.scores:
            if score.total == -1 and score.user_id == user_id:
                return True
        return False

    async def add_point(self, user_id: int) -> None:
        score = list(filter(lambda x: x.user_id.id == user_id, self.scores))[0]
        score.total += 1
        await self.app.store.games.add_one_point_to_score(score_id=score.id)
        user = list(filter(lambda x: x.id == user_id, self.users))[0]
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {user.full_name} получает 1 очко!"
        ))

    async def is_all_users_kicked(self):
        return all([self.is_user_kicked(user.id) for user in self.users])

    async def is_all_answers_used(self):
        return len(self.question.answers) == len(self.used_answers)

    async def is_correct_answer(self, answer: Answer) -> bool:
        answers = self.question.answers
        for answer_from_question in answers:
            if answer.title == answer_from_question.title:
                return True
        return False

    async def is_game_over(self) -> bool:
        game = await self.app.store.games.get_active_game_by_chat_id(self.chat_id)
        if game is None:
            return True
        return False

    async def check_answer(self, answer: Answer, user_id: int) -> None:
        if await self.is_correct_answer(answer):
            if answer.title in self.used_answers:
                await self.app.store.vk_api.send_group_message(Message(
                    receiver_id=self.chat_id,
                    text=f"Такой ответ уже был."
                ))
            else:
                self.used_answers.append(answer.title)
                self.game = await self.app.store.games.add_answer_to_used(answer.title)
                await self.add_point(user_id)
        else:
            await self.user_kick(user_id)

        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=2)

    async def end_game(self, chat_id: int):
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=5)
        self.state = self.STATES[5]

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

        self.game = None
        self.users = None
        self.scores = None
        self.question = None



