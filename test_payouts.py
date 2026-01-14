import pytest
from models import Card, Hand, BetHand
from payouts import PayoutResolver
from enums import GameResult


class TestPayoutResolver:
    def test_player_win_higher_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("8", 8))
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.WIN

    def test_player_lose_lower_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("6", 6))
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.LOSE

    def test_push_equal_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("7", 7))
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.PUSH

    def test_player_bust_loses(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("2", 2))
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.LOSE

    def test_dealer_bust_player_wins(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        # Dealer bust: value > 21
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("9", 9))
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.WIN

    def test_both_bust_player_loses(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        # Dealer bust: value > 21
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("5", 5))
        # Player also bust
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.LOSE  # Player bust takes precedence

    def test_player_blackjack_vs_20(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        # Dealer: 20
        
        player_hand = BetHand()
        player_hand.hand.add(Card("Ace", 11))
        player_hand.hand.add(Card("King", 10))
        # Player: 21 (blackjack)
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.WIN

    def test_push_with_21(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        dealer_hand.add(Card("6", 6))
        # Dealer: 21
        
        player_hand = BetHand()
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("5", 5))
        player_hand.hand.add(Card("6", 6))
        # Player: 21
        
        result = pr.resolve_hand(player_hand, dealer_hand)
        assert result == GameResult.PUSH
