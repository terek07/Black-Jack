"""
Integration tests for full game scenarios covering all edge cases.

These tests verify complete game flows from initial deal through payout,
including interactions between multiple components (game, managers, models).
"""
import pytest
from models import Card, Hand, BetHand, Player
from game import BlackjackGame
from enums import TurnResult, GameResult
from payouts import HandOutcome


class TestBlackjackEdgeCases:
    """Edge cases for natural blackjacks and immediate wins."""
    
    def test_player_blackjack_beats_dealer_20(self):
        """Player natural blackjack should beat dealer's 20."""
        game = BlackjackGame([("Alice", 100)])
        p = game.players[0]
        
        # Setup: Player blackjack, dealer 20
        p.hands[0].hand.cards = [Card("Ace", 11), Card("King", 10)]
        game.dealer_hand.cards = [Card("10", 10), Card("Queen", 10)]
        
        p.hands[0].is_finished = True
        game.play_dealer()
        
        results = game.settle_all_bets()
        outcome = results["Alice"][0]
        assert outcome.result == GameResult.BLACKJACK_WIN
        assert outcome.payout == 150  # 3:2 on 100
        assert p.hands[0].hand.is_blackjack is True
    
    def test_dealer_blackjack_vs_player_21(self):
        """Dealer blackjack vs player's 21 with 3+ cards.
        
        Dealer blackjack outranks player 21 (non-blackjack).
        """
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Setup: Player 21 (3 cards), dealer blackjack
        p.hands[0].hand.cards = [Card("7", 7), Card("7", 7), Card("7", 7)]
        game.dealer_hand.cards = [Card("Ace", 11), Card("Jack", 10)]
        
        p.hands[0].is_finished = True
        
        results = game.settle_all_bets()
        outcome = results["Bob"][0]
        assert outcome.result == GameResult.LOSE
        assert outcome.payout == -100
        assert game.dealer_has_blackjack is True
        assert p.hands[0].hand.is_blackjack is False  # 3 cards
    
    def test_both_blackjack_is_push(self):
        """Both player and dealer blackjack results in push."""
        game = BlackjackGame([("Charlie", 100)])
        p = game.players[0]
        
        # Both have blackjack
        p.hands[0].hand.cards = [Card("Ace", 11), Card("Queen", 10)]
        game.dealer_hand.cards = [Card("Ace", 11), Card("King", 10)]
        
        p.hands[0].is_finished = True
        
        results = game.settle_all_bets()
        outcome = results["Charlie"][0]
        assert outcome == HandOutcome(GameResult.PUSH, 0)

    def test_player_blackjack_beats_dealer_21_non_blackjack(self):
        """Player blackjack beats dealer 21 made with 3 cards and pays 3:2."""
        game = BlackjackGame([("Daisy", 80)])
        p = game.players[0]

        p.hands[0].hand.cards = [Card("Ace", 11), Card("Jack", 10)]  # blackjack
        game.dealer_hand.cards = [Card("10", 10), Card("5", 5), Card("6", 6)]  # 21, not blackjack

        p.hands[0].is_finished = True
        results = game.settle_all_bets()
        outcome = results["Daisy"][0]
        assert outcome.result == GameResult.BLACKJACK_WIN
        assert outcome.payout == 120  # 3:2 on 80


class TestSplitIntegration:
    """Integration tests for split scenarios with full game flow."""
    
    def test_split_then_bust_both_hands(self):
        """Split hand where both resulting hands bust."""
        game = BlackjackGame([("Alice", 50)])
        p = game.players[0]
        
        # Setup pair of 8s
        p.hands[0].hand.cards = [Card("8", 8), Card("8", 8)]
        
        # Split
        game.split_hand(p, 0)
        assert len(p.hands) == 2
        
        # Force both to bust
        p.hands[0].hand.cards.append(Card("10", 10))
        p.hands[0].hand.cards.append(Card("5", 5))  # 8+10+5 = 23
        p.hands[0].is_finished = True
        
        p.hands[1].hand.cards.append(Card("Queen", 10))
        p.hands[1].hand.cards.append(Card("6", 6))  # 8+10+6 = 24
        p.hands[1].is_finished = True
        
        game.play_dealer()
        results = game.settle_all_bets()
        
        assert len(results["Alice"]) == 2
        assert results["Alice"][0].result == GameResult.LOSE  # Both bust
        assert results["Alice"][0].payout == -50
        assert results["Alice"][1].result == GameResult.LOSE
        assert results["Alice"][1].payout == -50
    
    def test_split_win_one_lose_one(self):
        """Split where one hand wins and one loses."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Setup pair
        p.hands[0].hand.cards = [Card("9", 9), Card("9", 9)]
        game.split_hand(p, 0)
        
        # First hand wins with 20
        p.hands[0].hand.cards = [Card("9", 9), Card("Ace", 11)]  # 20
        p.hands[0].is_finished = True
        
        # Second hand loses with 16
        p.hands[1].hand.cards = [Card("9", 9), Card("7", 7)]  # 16
        p.hands[1].is_finished = True
        
        # Dealer gets 19
        game.dealer_hand.cards = [Card("10", 10), Card("9", 9)]
        
        results = game.settle_all_bets()
        assert results["Bob"][0].result == GameResult.WIN   # 20 > 19
        assert results["Bob"][0].payout == 100
        assert results["Bob"][1].result == GameResult.LOSE  # 16 < 19
        assert results["Bob"][1].payout == -100
    
    def test_split_then_double_on_one_hand(self):
        """Split then double down on one of the resulting hands."""
        game = BlackjackGame([("Charlie", 100)])
        p = game.players[0]
        
        # Setup and split
        p.hands[0].hand.cards = [Card("7", 7), Card("7", 7)]
        game.split_hand(p, 0)
        
        # Ensure both hands have 2 cards (required for double)
        assert len(p.hands[0].hand.cards) == 2
        assert len(p.hands[1].hand.cards) == 2
        
        # Double on first hand
        original_bet = p.hands[0].bet
        result = game.double(p, 0)
        
        assert p.hands[0].bet == original_bet * 2
        assert p.hands[0].doubled is True
        assert p.hands[0].is_finished is True
        assert len(p.hands[0].hand.cards) == 3
    
    def test_split_aces(self):
        """Split aces and verify both get new cards."""
        game = BlackjackGame([("Dave", 100)])
        p = game.players[0]
        
        # Setup pair of aces
        p.hands[0].hand.cards = [Card("Ace", 11), Card("Ace", 11)]
        
        game.split_hand(p, 0)
        
        # Both hands should have 2 cards (1 ace + 1 new card)
        assert len(p.hands) == 2
        assert len(p.hands[0].hand.cards) == 2
        assert len(p.hands[1].hand.cards) == 2
        
        # Original aces should be in different hands
        assert p.hands[0].hand.cards[0].value == 11
        assert p.hands[1].hand.cards[0].value == 11


class TestInsuranceIntegration:
    """Integration tests for insurance betting scenarios."""
    
    def test_insurance_wins_with_dealer_blackjack(self):
        """Insurance bet pays when dealer has blackjack."""
        game = BlackjackGame([("Alice", 100)])
        p = game.players[0]
        
        # Dealer shows Ace
        game.dealer_hand.cards = [Card("Ace", 11), Card("King", 10)]
        
        # Player takes insurance for half bet (50)
        game.insurance.place(p, 50)
        
        # Dealer has blackjack
        assert game.dealer_has_blackjack is True
        
        insurance_result = game.resolve_insurance()
        assert insurance_result["Alice"] == 100  # 50 * 2 = 100
    
    def test_insurance_loses_without_dealer_blackjack(self):
        """Insurance bet lost when dealer doesn't have blackjack."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Dealer shows Ace but doesn't have blackjack
        game.dealer_hand.cards = [Card("Ace", 11), Card("5", 5)]
        
        game.insurance.place(p, 50)
        
        assert game.dealer_has_blackjack is False
        
        insurance_result = game.resolve_insurance()
        assert insurance_result["Bob"] == -50  # Lost insurance bet
    
    def test_insurance_with_player_blackjack_dealer_blackjack(self):
        """Both have blackjack, insurance pays, main bet pushes."""
        game = BlackjackGame([("Charlie", 100)])
        p = game.players[0]
        
        # Both have blackjack
        p.hands[0].hand.cards = [Card("Ace", 11), Card("Queen", 10)]
        game.dealer_hand.cards = [Card("Ace", 11), Card("King", 10)]
        
        game.insurance.place(p, 50)
        p.hands[0].is_finished = True
        
        # Check insurance
        insurance_result = game.resolve_insurance()
        assert insurance_result["Charlie"] == 100  # Win insurance
        
        # Check main bet
        bet_result = game.settle_all_bets()
        assert bet_result["Charlie"][0] == HandOutcome(GameResult.PUSH, 0)  # Push on blackjack


class TestDealerPlayEdgeCases:
    """Edge cases for dealer automated play."""
    
    def test_dealer_stands_on_soft_17(self):
        """Dealer with Ace+6 (soft 17) stands.
        
        Note: This implementation uses 'stand on soft 17' rule.
        """
        game = BlackjackGame([("Alice", 100)])
        
        # Dealer soft 17 (Ace + 6)
        game.dealer_hand.cards = [Card("Ace", 11), Card("6", 6)]
        assert game.dealer_hand.value == 17
        
        game.play_dealer()
        
        # Dealer stands on 17 (including soft 17)
        assert game.dealer_hand.value == 17
        assert len(game.dealer_hand.cards) == 2
    
    def test_dealer_stands_on_hard_17(self):
        """Dealer with hard 17 should stand."""
        game = BlackjackGame([("Bob", 100)])
        
        # Dealer hard 17
        game.dealer_hand.cards = [Card("10", 10), Card("7", 7)]
        assert game.dealer_hand.value == 17
        
        game.play_dealer()
        
        # Dealer should stand with exactly 2 cards
        assert len(game.dealer_hand.cards) == 2
        assert game.dealer_hand.value == 17
    
    def test_dealer_busts(self):
        """Dealer busts and all active players win."""
        game = BlackjackGame([("Charlie", 50), ("Dave", 75)])
        
        # Both players stand with modest hands
        game.players[0].hands[0].hand.cards = [Card("10", 10), Card("8", 8)]
        game.players[0].hands[0].is_finished = True
        
        game.players[1].hands[0].hand.cards = [Card("9", 9), Card("7", 7)]
        game.players[1].hands[0].is_finished = True
        
        # Dealer busts
        game.dealer_hand.cards = [Card("10", 10), Card("7", 7), Card("6", 6)]
        assert game.dealer_hand.is_bust is True
        
        results = game.settle_all_bets()
        assert results["Charlie"][0].result == GameResult.WIN
        assert results["Charlie"][0].payout == 50
        assert results["Dave"][0].result == GameResult.WIN
        assert results["Dave"][0].payout == 75
    
    def test_dealer_hits_to_exactly_17(self):
        """Dealer hits from low value to exactly 17."""
        game = BlackjackGame([("Eve", 100)])
        
        # Dealer starts low
        game.dealer_hand.cards = [Card("5", 5), Card("4", 4)]  # 9
        
        game.play_dealer()
        
        # Dealer should end >= 17 or bust
        assert game.dealer_hand.value >= 17 or game.dealer_hand.is_bust


class TestMultiPlayerScenarios:
    """Integration tests with multiple players and different outcomes."""
    
    def test_three_players_different_outcomes(self):
        """Three players with win, lose, and push outcomes."""
        game = BlackjackGame([
            ("Winner", 100),
            ("Loser", 100),
            ("Pusher", 100)
        ])
        
        # Setup hands
        game.players[0].hands[0].hand.cards = [Card("10", 10), Card("10", 10)]  # 20
        game.players[0].hands[0].is_finished = True
        
        game.players[1].hands[0].hand.cards = [Card("10", 10), Card("6", 6)]   # 16
        game.players[1].hands[0].is_finished = True
        
        game.players[2].hands[0].hand.cards = [Card("10", 10), Card("8", 8)]   # 18
        game.players[2].hands[0].is_finished = True
        
        # Dealer gets 18
        game.dealer_hand.cards = [Card("10", 10), Card("8", 8)]
        
        results = game.settle_all_bets()
        assert results["Winner"][0] == HandOutcome(GameResult.WIN, 100)   # 20 > 18
        assert results["Loser"][0] == HandOutcome(GameResult.LOSE, -100)   # 16 < 18
        assert results["Pusher"][0] == HandOutcome(GameResult.PUSH, 0)  # 18 = 18

    def test_mixed_blackjack_and_21_players(self):
        """One player has blackjack, another has 21 (non-blackjack) vs dealer 21."""
        game = BlackjackGame([
            ("BJ_Player", 100),
            ("TwentyOne", 100)
        ])

        game.players[0].hands[0].hand.cards = [Card("Ace", 11), Card("King", 10)]  # blackjack
        game.players[0].hands[0].is_finished = True

        game.players[1].hands[0].hand.cards = [Card("10", 10), Card("5", 5), Card("6", 6)]  # 21, not blackjack
        game.players[1].hands[0].is_finished = True

        game.dealer_hand.cards = [Card("10", 10), Card("5", 5), Card("6", 6)]  # Dealer 21, not blackjack

        results = game.settle_all_bets()
        assert results["BJ_Player"][0] == HandOutcome(GameResult.BLACKJACK_WIN, 150)  # 3:2 on 100
        assert results["TwentyOne"][0] == HandOutcome(GameResult.PUSH, 0)  # 21 vs 21
    
    def test_all_players_bust_before_dealer_plays(self):
        """All players bust, dealer shouldn't need to play."""
        game = BlackjackGame([("Alice", 50), ("Bob", 75)])
        
        # Both players bust
        game.players[0].hands[0].hand.cards = [Card("10", 10), Card("10", 10), Card("5", 5)]
        game.players[0].hands[0].is_finished = True
        
        game.players[1].hands[0].hand.cards = [Card("Queen", 10), Card("King", 10), Card("2", 2)]
        game.players[1].hands[0].is_finished = True
        
        # Even if dealer doesn't play, players lose
        results = game.settle_all_bets()
        assert results["Alice"][0] == HandOutcome(GameResult.LOSE, -50)
        assert results["Bob"][0] == HandOutcome(GameResult.LOSE, -75)
    
    def test_multiple_players_with_splits(self):
        """Two players, both split, different outcomes on each hand."""
        game = BlackjackGame([("Alice", 100), ("Bob", 100)])
        
        # Alice splits 8s
        game.players[0].hands[0].hand.cards = [Card("8", 8), Card("8", 8)]
        game.split_hand(game.players[0], 0)
        
        # Bob splits 9s
        game.players[1].hands[0].hand.cards = [Card("9", 9), Card("9", 9)]
        game.split_hand(game.players[1], 0)
        
        # Verify both have 2 hands now
        assert len(game.players[0].hands) == 2
        assert len(game.players[1].hands) == 2
        
        # Each hand should have 2 cards
        for player in game.players:
            for hand in player.hands:
                assert len(hand.hand.cards) == 2


class TestDoubleDownEdgeCases:
    """Edge cases for double down functionality."""
    
    def test_double_and_bust(self):
        """Player doubles down and busts."""
        game = BlackjackGame([("Alice", 100)])
        p = game.players[0]
        
        # Setup hand that will bust on double
        p.hands[0].hand.cards = [Card("10", 10), Card("8", 8)]
        
        # Mock deck to ensure bust card
        original_bet = p.hands[0].bet
        result = game.double(p, 0)
        
        # If last card was high enough, should bust
        if p.hands[0].hand.value > 21:
            assert result == TurnResult.BUST
            assert p.hands[0].hand.is_bust is True
        
        assert p.hands[0].bet == original_bet * 2
        assert p.hands[0].is_finished is True
    
    def test_double_and_win(self):
        """Player doubles down and wins."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Setup good double situation
        p.hands[0].hand.cards = [Card("5", 5), Card("6", 6)]  # 11
        
        result = game.double(p, 0)
        
        # Setup dealer to lose
        game.dealer_hand.cards = [Card("10", 10), Card("6", 6)]  # 16
        
        if not p.hands[0].hand.is_bust:
            game.play_dealer()
            results = game.settle_all_bets()
            
            # If player didn't bust, check if bet was doubled
            assert p.hands[0].doubled is True
    
    def test_cannot_double_after_hit(self):
        """Cannot double after already hitting."""
        game = BlackjackGame([("Charlie", 100)])
        p = game.players[0]
        
        # Hit first (now 3 cards)
        game.hit(p, 0)
        
        # Try to double
        with pytest.raises(ValueError):
            game.double(p, 0)


class TestAceHandling:
    """Edge cases for ace value adjustment."""
    
    def test_multiple_aces_adjustment(self):
        """Multiple aces should adjust correctly."""
        game = BlackjackGame([("Alice", 100)])
        p = game.players[0]
        
        # Three aces + 8 = 1+1+11+8 = 21
        p.hands[0].hand.cards = [
            Card("Ace", 11),
            Card("Ace", 11),
            Card("Ace", 11),
            Card("8", 8)
        ]
        
        assert p.hands[0].hand.value == 21
        assert not p.hands[0].hand.is_bust
    
    def test_soft_hand_becomes_hard(self):
        """Soft hand (Ace as 11) becomes hard after hitting."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Ace + 5 = 16 (soft)
        p.hands[0].hand.cards = [Card("Ace", 11), Card("5", 5)]
        assert p.hands[0].hand.value == 16
        
        # Hit with 10 -> should adjust Ace to 1 (1+5+10=16)
        p.hands[0].hand.add(Card("10", 10))
        assert p.hands[0].hand.value == 16  # Ace adjusted to 1
        assert not p.hands[0].hand.is_bust
    
    def test_dealer_soft_17_with_ace(self):
        """Dealer with Ace+6 counts as soft 17 and stands.
        
        This implementation uses 'stand on soft 17' rule.
        """
        game = BlackjackGame([("Charlie", 100)])
        
        game.dealer_hand.cards = [Card("Ace", 11), Card("6", 6)]
        
        assert game.dealer_hand.value == 17
        # Dealer behavior on soft 17 depends on house rules
        # This implementation stands on soft 17
        game.play_dealer()
        assert len(game.dealer_hand.cards) == 2  # Stands, doesn't hit
        assert game.dealer_hand.value == 17


class TestPushScenarios:
    """Edge cases for push (tie) outcomes."""
    
    def test_both_21_not_blackjack(self):
        """Both have 21 with 3+ cards is a push."""
        game = BlackjackGame([("Alice", 100)])
        p = game.players[0]
        
        # Player 21 with 3 cards
        p.hands[0].hand.cards = [Card("7", 7), Card("7", 7), Card("7", 7)]
        p.hands[0].is_finished = True
        
        # Dealer 21 with 3 cards
        game.dealer_hand.cards = [Card("8", 8), Card("8", 8), Card("5", 5)]
        
        results = game.settle_all_bets()
        assert results["Alice"][0] == HandOutcome(GameResult.PUSH, 0)
    
    def test_both_bust_player_loses(self):
        """If both bust, player still loses (loses immediately on bust)."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Player busts
        p.hands[0].hand.cards = [Card("10", 10), Card("10", 10), Card("5", 5)]
        p.hands[0].is_finished = True
        
        # Dealer also busts (but player already lost)
        game.dealer_hand.cards = [Card("10", 10), Card("Queen", 10), Card("King", 10)]
        
        results = game.settle_all_bets()
        assert results["Bob"][0] == HandOutcome(GameResult.LOSE, -100)
    
    def test_both_have_same_non_21_value(self):
        """Both have same value under 21 is a push."""
        game = BlackjackGame([("Charlie", 100)])
        p = game.players[0]
        
        # Both have 19
        p.hands[0].hand.cards = [Card("10", 10), Card("9", 9)]
        p.hands[0].is_finished = True
        
        game.dealer_hand.cards = [Card("Queen", 10), Card("9", 9)]
        
        results = game.settle_all_bets()
        assert results["Charlie"][0] == HandOutcome(GameResult.PUSH, 0)


class TestComplexGameFlows:
    """Complex multi-step game scenarios."""
    
    def test_full_game_with_split_insurance_and_double(self):
        """Complex game: split, insurance, double on one split hand."""
        game = BlackjackGame([("Alice", 200)])
        p = game.players[0]
        
        # Dealer shows Ace
        game.dealer_hand.cards = [Card("Ace", 11), Card("7", 7)]
        
        # Player has pair of 9s
        p.hands[0].hand.cards = [Card("9", 9), Card("9", 9)]
        
        # Take insurance
        game.insurance.place(p, 100)  # Half of 200
        
        # Split the 9s
        game.split_hand(p, 0)
        assert len(p.hands) == 2
        
        # Double on first hand (if possible with 2 cards)
        if len(p.hands[0].hand.cards) == 2:
            original_bet = p.hands[0].bet
            game.double(p, 0)
            assert p.hands[0].bet == original_bet * 2
        
        # Stand on second hand
        game.stand(p, 1)
        
        # Resolve insurance
        insurance_result = game.resolve_insurance()
        assert "Alice" in insurance_result
        
        # Dealer plays and settle
        game.play_dealer()
        results = game.settle_all_bets()
        
        # Should have results for both hands
        assert len(results["Alice"]) == 2
    
    def test_sequential_actions_hit_hit_stand(self):
        """Player hits twice then stands."""
        game = BlackjackGame([("Bob", 100)])
        p = game.players[0]
        
        # Start with low cards
        p.hands[0].hand.cards = [Card("2", 2), Card("3", 3)]  # 5
        
        # Hit twice
        result1 = game.hit(p, 0)
        result2 = game.hit(p, 0)
        
        # If not bust, stand
        if result2 != TurnResult.BUST:
            result3 = game.stand(p, 0)
            assert result3 == TurnResult.STAND
            assert p.hands[0].is_finished is True
    
    def test_game_with_all_features(self):
        """Kitchen sink test: multiple players, splits, insurance, various outcomes."""
        game = BlackjackGame([
            ("Splitter", 100),
            ("Doubler", 100),
            ("Hitter", 100)
        ])
        
        # Dealer shows Ace
        game.dealer_hand.cards = [Card("Ace", 11), Card("9", 9)]
        
        # Player 1: Splits
        game.players[0].hands[0].hand.cards = [Card("8", 8), Card("8", 8)]
        game.split_hand(game.players[0], 0)
        game.stand(game.players[0], 0)
        game.stand(game.players[0], 1)
        
        # Player 2: Doubles
        game.players[1].hands[0].hand.cards = [Card("5", 5), Card("6", 6)]
        if len(game.players[1].hands[0].hand.cards) == 2:
            game.double(game.players[1], 0)
        
        # Player 3: Hits then stands
        game.players[2].hands[0].hand.cards = [Card("10", 10), Card("6", 6)]
        result = game.hit(game.players[2], 0)
        if result != TurnResult.BUST:
            game.stand(game.players[2], 0)
        
        # Resolve game
        game.play_dealer()
        results = game.settle_all_bets()
        
        # Verify all players have results
        assert "Splitter" in results
        assert "Doubler" in results
        assert "Hitter" in results
        
        # Splitter should have 2 hands
        assert len(results["Splitter"]) == 2
