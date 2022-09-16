import asyncio
from typing import Optional, List, TYPE_CHECKING, Tuple
from sqlalchemy.exc import IntegrityError

from app.game.models import User, Score, Game
from app.quiz.schemes import Question, Answer
from app.store.vk_api.dataclasses import Message

if TYPE_CHECKING:
    from app.web.app import Application


def run_async_func(coro):
    task = asyncio.create_task(coro)


class GameManager:
    STATES = {
        1: "started",
        2: "question",
        3: "waiting",
        4: "checking",
        5: "done"
        }

    def __init__(self, app: "Application", game: Game = None) -> None:
        self.app = app
        if game is None:
            self.game: Optional[Game] = None
            self.question: Optional[Question] = None
            self.state: Optional[str] = None
            self.chat_id: Optional[int] = None
            self.scores: Optional[List[Score]] = None
            self.users: Optional[List[User]] = None
            self.used_answers: Optional[List[str]] = None
            self.answers: Optional[List[Answer]] = None
        else:
            run_async_func(self.init_from_game(game))

    async def init_from_game(self, game: Game) -> None:
        self.game = game
        self.question = await self.app.store.quizzes.get_question_by_id(
            game.question_id)
        self.state = game.state_id
        self.chat_id = game.chat_id
        self.scores = await self.app.store.games.get_scores_by_game_id(game.id)
        self.users = await self.app.store.vk_api.get_conversation_members(
            peer_id=game.chat_id)
        self.answers = await self.app.store.quizzes.get_answers_by_question_id(self.question.id)
        self.used_answers = self.game.used_answers
        if self.used_answers is None:
            self.used_answers = []

    async def start_game(self, chat_id: int) -> None:
        self.state = 1
        self.chat_id = chat_id
        self.users = await self.app.store.vk_api.get_conversation_members(peer_id=chat_id)
        self.game = await self.app.store.games.create_game(chat_id=chat_id)
        self.question = await self.app.store.quizzes.get_question_by_id(self.game.question_id)
        self.answers = await self.app.store.quizzes.get_answers_by_question_id(self.question.id)
        self.used_answers = []
        for user in self.users:
            try:
                await self.app.store.games.create_user(user.id, user.full_name)
            except IntegrityError:
                pass
        self.scores = await self.app.store.games.create_start_scores(
            game_id=self.game.id,
            users_id=[user.id for user in self.users]
        )
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=chat_id,
            text=f'Добрый день! Начинаем игру 100 к 1. Игра № {self.game.id}, участники: '
                 f'{",".join([user.full_name for user in self.users])}'
        ))
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=2)
        self.state = 2

    async def send_question(self) -> None:
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.game.chat_id,
            text=f"{self.question.title}"
        ))
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=3)
        self.state = 3

    async def user_kick(self, user_id: int) -> None:
        for score in self.scores:
            if score.user_id == user_id:
                print('SCORE: ', score)
                score.total = -1
                await self.app.store.games.update_score_to_minus_one_point(score.id)

        lose_user = list(filter(lambda x: x.id == user_id, self.users))[0]
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {lose_user.full_name} выбывает!"
        ))

    async def is_user_kicked(self, user_id: int) -> bool:
        if self.scores is None:
            return False
        for score in self.scores:
            if score.total == -1 and score.user_id == user_id:
                return True
        return False

    async def add_point(self, user_id: int) -> None:
        for score in self.scores:
            if score.user_id == user_id:
                score.total += 1
                score_obj = score

        await self.app.store.games.update_total_in_score(score_id=score_obj.id, total=score_obj.total)

        for user in self.users:
            if user.id == user_id:
                user_from_game = user
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f"Игрок {user_from_game.full_name} получает 1 очко!"
        ))

    async def is_all_users_kicked(self):
        if self.scores is None:
            return False
        count = 0
        for score in self.scores:
            if score.total == -1:
                count += 1
        if count == len(self.scores):
            return True
        return False

    async def is_all_answers_used(self):
        if self.question is None:
            return False
        return len(self.question.answers) == len(self.used_answers)

    async def is_correct_answer(self, answer: Answer) -> bool:
        answers = self.answers
        print('RIGHT ANSWERS:', answers)
        print("YOUR ANSWER:", answer)
        for answer_from_question in answers:
            if answer.title.lower() == answer_from_question.title.lower():
                return True
        return False

    async def is_game_over(self) -> bool:
        game = await self.app.store.games.get_active_game_by_chat_id(self.chat_id)
        if game is None:
            return True
        return False

    async def prepare_to_answer(self, user_id: int) -> None:
        for user in self.users:
            if user.id == user_id:
                answer_user = user
        await self.app.store.vk_api.send_group_message(Message(
            receiver_id=self.chat_id,
            text=f'{answer_user.full_name}, жду твой ответ!'
        ))

    async def check_answer(self, answer: Answer, user_id: int) -> None:
        if await self.is_correct_answer(answer):
            if answer.title in self.used_answers:
                await self.app.store.vk_api.send_group_message(Message(
                    receiver_id=self.chat_id,
                    text=f"Такой ответ уже был."
                ))
            else:
                self.used_answers.append(answer.title)
                self.game = await self.app.store.games.add_answer_to_used(
                    game_id=self.game.id, answer=answer.title)
                await self.add_point(user_id)
        else:
            await self.user_kick(user_id)
        self.state = 3
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=3)

    async def end_game(self, chat_id: int):
        self.game = await self.app.store.games.update_state_in_game(game_id=self.game.id, state_id=5)
        self.state = 5
        results = ''
        for score in self.scores:
            for user in self.users:
                if user.id == score.user_id:
                    results += f'{user.full_name}: {score.total} '

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
        self.chat_id = None
        self.used_answers = None



