from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Card:
    name: str
    value: int


@dataclass
class Hand:
    cards: List[Card] = field(default_factory=list)

    def add(self, card: Card):
        self.cards.append(card)

    @property
    def value(self) -> int:
        total = 0
        aces = 0
        for c in self.cards:
            total += c.value
            if c.value == 11:
                aces += 1
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_bust(self) -> bool:
        return self.value > 21


@dataclass
class BetHand:
    hand: Hand = field(default_factory=Hand)
    bet: int = 0
    is_finished: bool = False
    doubled: bool = False


@dataclass
class Player:
    name: str
    hands: List[BetHand] = field(default_factory=list)
    insurance_bet: int = 0
    balance: int = 1000
