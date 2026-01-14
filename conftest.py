import pytest
from models import Card, Hand, BetHand, Player
from deck import Deck


@pytest.fixture
def fresh_deck():
    return Deck()


@pytest.fixture
def single_player():
    player = Player(name="Alice", hands=[BetHand(bet=10)])
    player.hands[0].hand.add(Card("5 of Hearts", 5))
    player.hands[0].hand.add(Card("6 of Diamonds", 6))
    return player


@pytest.fixture
def blackjack_hand():
    hand = Hand()
    hand.add(Card("Ace of Spades", 11))
    hand.add(Card("King of Hearts", 10))
    return hand


@pytest.fixture
def bust_hand():
    hand = Hand()
    hand.add(Card("10 of Hearts", 10))
    hand.add(Card("Queen of Spades", 10))
    hand.add(Card("2 of Clubs", 2))
    return hand
