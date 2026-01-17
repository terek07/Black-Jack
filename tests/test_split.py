import pytest
from engine.models import Card, BetHand, Hand
from engine.split import SplitManager


class TestSplitManager:
    def test_can_split_identical_numbered_cards(self):
        sm = SplitManager()
        hand = BetHand(bet=10)
        hand.hand.add(Card("8 of Hearts", 8))
        hand.hand.add(Card("8 of Diamonds", 8))
        assert sm.can_split(hand) is True

    def test_can_split_identical_face_cards(self):
        sm = SplitManager()
        hand = BetHand(bet=10)
        hand.hand.add(Card("King", 10))
        hand.hand.add(Card("Queen", 10))
        # Note: Kings and Queens have same value (10) but different names
        # The implementation checks value, not name
        assert sm.can_split(hand) is True

    def test_can_split_aces(self):
        sm = SplitManager()
        hand = BetHand(bet=10)
        hand.hand.add(Card("Ace of Hearts", 11))
        hand.hand.add(Card("Ace of Spades", 11))
        assert sm.can_split(hand) is True

    def test_cannot_split_different_values(self):
        sm = SplitManager()
        hand = BetHand()
        hand.hand.add(Card("8", 8))
        hand.hand.add(Card("9", 9))
        assert sm.can_split(hand) is False

    def test_cannot_split_single_card(self):
        sm = SplitManager()
        hand = BetHand()
        hand.hand.add(Card("8", 8))
        assert sm.can_split(hand) is False

    def test_cannot_split_three_cards(self):
        sm = SplitManager()
        hand = BetHand()
        hand.hand.add(Card("8", 8))
        hand.hand.add(Card("8", 8))
        hand.hand.add(Card("5", 5))
        assert sm.can_split(hand) is False

    def test_split_creates_two_hands(self):
        sm = SplitManager()
        hand = BetHand(bet=10)
        hand.hand.add(Card("8 of Hearts", 8))
        hand.hand.add(Card("8 of Diamonds", 8))
        
        h1, h2 = sm.split(hand)
        assert len(h1.hand.cards) == 1
        assert len(h2.hand.cards) == 1

    def test_split_preserves_bet(self):
        sm = SplitManager()
        hand = BetHand(bet=25)
        hand.hand.add(Card("7", 7))
        hand.hand.add(Card("7", 7))
        
        h1, h2 = sm.split(hand)
        assert h1.bet == 25
        assert h2.bet == 25

    def test_split_creates_new_hands(self):
        sm = SplitManager()
        hand = BetHand(bet=10)
        hand.hand.add(Card("6 of Hearts", 6))
        hand.hand.add(Card("6 of Diamonds", 6))
        
        h1, h2 = sm.split(hand)
        # h1 and h2 should be different BetHand objects
        assert h1 is not h2
        assert h1.hand is not h2.hand

    def test_split_raises_error_on_invalid_hand(self):
        sm = SplitManager()
        hand = BetHand()
        hand.hand.add(Card("8", 8))
        hand.hand.add(Card("9", 9))
        with pytest.raises(ValueError):
            sm.split(hand)
