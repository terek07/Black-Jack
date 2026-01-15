from enum import Enum


class TurnResult(Enum):
    CONTINUE = "continue"
    BUST = "bust"
    BLACKJACK = "blackjack"
    STAND = "stand"
    DOUBLE = "double"


class GameResult(Enum):
    WIN = "win"
    LOSE = "lose"
    PUSH = "push"
    BLACKJACK_WIN = "blackjack_win"
