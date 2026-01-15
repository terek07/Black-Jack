import pytest
from models import Card, Hand, BetHand
from payouts import PayoutResolver, HandOutcome
from enums import GameResult


class TestPayoutResolver:
    def test_player_win_higher_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("8", 8))
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.WIN, 10)

    def test_player_lose_lower_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("6", 6))
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.LOSE, -10)

    def test_push_equal_value(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("7", 7))
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.PUSH, 0)

    def test_player_bust_loses(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("2", 2))
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.LOSE, -10)

    def test_dealer_bust_player_wins(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        # Dealer bust: value > 21
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("9", 9))
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.WIN, 10)

    def test_both_bust_player_loses(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        # Dealer bust: value > 21
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("5", 5))
        # Player also bust
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.LOSE, -10)  # Player bust takes precedence

    def test_player_blackjack_vs_20(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("10", 10))
        # Dealer: 20
        
        player_hand = BetHand(bet=20)
        player_hand.hand.add(Card("Ace", 11))
        player_hand.hand.add(Card("King", 10))
        # Player: 21 (blackjack)
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.BLACKJACK_WIN, 30)  # 3:2 payout on 20

    def test_push_with_21(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        dealer_hand.add(Card("6", 6))
        # Dealer: 21
        
        player_hand = BetHand(bet=10)
        player_hand.hand.add(Card("10", 10))
        player_hand.hand.add(Card("5", 5))
        player_hand.hand.add(Card("6", 6))
        # Player: 21
        
        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.PUSH, 0)

    def test_dealer_blackjack_vs_player_21_non_blackjack(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("Ace", 11))
        dealer_hand.add(Card("King", 10))  # Dealer blackjack

        player_hand = BetHand(bet=25)
        player_hand.hand.add(Card("9", 9))
        player_hand.hand.add(Card("7", 7))
        player_hand.hand.add(Card("5", 5))  # Player 21, not blackjack

        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.LOSE, -25)

    def test_player_blackjack_vs_dealer_21_non_blackjack(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        dealer_hand.add(Card("6", 6))  # Dealer 21, not blackjack

        player_hand = BetHand(bet=40)
        player_hand.hand.add(Card("Ace", 11))
        player_hand.hand.add(Card("Queen", 10))  # Player blackjack

        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.BLACKJACK_WIN, 60)  # 3:2 on 40

    def test_both_blackjack_push(self):
        pr = PayoutResolver()
        dealer_hand = Hand()
        dealer_hand.add(Card("Ace", 11))
        dealer_hand.add(Card("King", 10))  # Dealer blackjack

        player_hand = BetHand(bet=30)
        player_hand.hand.add(Card("Ace", 11))
        player_hand.hand.add(Card("Queen", 10))  # Player blackjack

        outcome = pr.resolve_hand(player_hand, dealer_hand)
        assert outcome == HandOutcome(GameResult.PUSH, 0)
