import random
from models import Card


class Deck:
    def __init__(self):
        self.cards = self._create()
        random.shuffle(self.cards)

    def _create(self):
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
