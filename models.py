import random
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Card:
    name: str
    value: int


class Deck:
    def __init__(self):
        self.cards = self._create_deck()
        random.shuffle(self.cards)

    def _create_deck(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = [
            ("Ace", 11), ("2", 2), ("3", 3), ("4", 4), ("5", 5),
            ("6", 6), ("7", 7), ("8", 8), ("9", 9),
            ("10", 10), ("Jack", 10), ("Queen", 10), ("King", 10),
        ]
        return [
            Card(f"{rank} of {suit}", value)
            for suit in suits
            for rank, value in ranks
        ]

    def draw(self) -> Card:
        return self.cards.pop()


@dataclass
class Hand:
    cards: List[Card] = field(default_factory=list)

    def add_card(self, card: Card):
        self.cards.append(card)

    @property
    def value(self) -> int:
        total = 0
        aces = 0

        for card in self.cards:
            total += card.value
            if card.value == 11:
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
class Player:
    name: str
    hand: Hand = field(default_factory=Hand)
    bet: int = 0
