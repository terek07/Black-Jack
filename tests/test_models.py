import pytest
from engine.models import Card, Hand


class TestHandValueCalculation:
    def test_hand_value_simple(self):
        hand = Hand()
        hand.add(Card("5", 5))
        hand.add(Card("6", 6))
        assert hand.value == 11

    def test_hand_value_single_ace_below_21(self):
        hand = Hand()
        hand.add(Card("Ace", 11))
        hand.add(Card("5", 5))
        assert hand.value == 16  # Ace counts as 11

    def test_hand_value_single_ace_above_21(self):
        hand = Hand()
        hand.add(Card("Ace", 11))
        hand.add(Card("10", 10))
        hand.add(Card("5", 5))
        assert hand.value == 16  # Ace adjusts to 1: 1 + 10 + 5

    def test_hand_value_multiple_aces(self):
        hand = Hand()
        hand.add(Card("Ace", 11))
        hand.add(Card("Ace", 11))
        hand.add(Card("9", 9))
        assert hand.value == 21  # Two aces adjust to 1 + 11 + 9

    def test_hand_value_three_aces(self):
        hand = Hand()
        hand.add(Card("Ace", 11))
        hand.add(Card("Ace", 11))
        hand.add(Card("Ace", 11))
        assert hand.value == 13  # All three aces adjust: 1 + 1 + 11

    def test_hand_value_face_cards(self):
        hand = Hand()
        hand.add(Card("King", 10))
        hand.add(Card("Queen", 10))
        assert hand.value == 20

    def test_blackjack_detection(self, blackjack_hand):
        assert blackjack_hand.is_blackjack is True
        assert blackjack_hand.is_bust is False

    def test_bust_detection(self, bust_hand):
        assert bust_hand.is_bust is True
        assert bust_hand.is_blackjack is False

    def test_hand_with_21_but_not_blackjack(self):
        hand = Hand()
        hand.add(Card("10", 10))
        hand.add(Card("5", 5))
        hand.add(Card("6", 6))
        assert hand.value == 21
        assert hand.is_blackjack is False  # Not blackjack (more than 2 cards)

    def test_empty_hand(self):
        hand = Hand()
        assert hand.value == 0
        assert hand.is_blackjack is False
        assert hand.is_bust is False
