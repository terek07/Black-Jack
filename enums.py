from enum import Enum


class TurnResult(Enum):
    CONTINUE = "continue"
    BUST = "bust"
    BLACKJACK = "blackjack"
    STAND = "stand"


class GameResult(Enum):
    WIN = "win"
    LOSE = "lose"
    PUSH = "push"
