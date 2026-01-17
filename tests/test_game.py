import pytest
from engine.models import Card
from engine.game import BlackjackGame
from engine.enums import TurnResult, GameResult


class TestBlackjackGame:
    def test_initial_setup_single_player(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        assert len(game.players) == 1
        assert game.players[0].name == "Alice"
        assert len(game.players[0].hands[0].hand.cards) == 2
        assert game.players[0].hands[0].bet == 10

    def test_initial_setup_multiple_players(self):
        players = [("Alice", 10), ("Bob", 20), ("Charlie", 15)]
        game = BlackjackGame(players)
        
        assert len(game.players) == 3
        for i, (name, bet) in enumerate(players):
            assert game.players[i].name == name
            assert game.players[i].hands[0].bet == bet

    def test_dealer_has_two_initial_cards(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        assert len(game.dealer_hand.cards) == 2

    def test_dealer_has_blackjack(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        game.dealer_hand.cards = [Card("Ace", 11), Card("King", 10)]
        assert game.dealer_has_blackjack is True

    def test_dealer_no_blackjack_with_21(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        game.dealer_hand.cards = [Card("10", 10), Card("5", 5), Card("6", 6)]
        assert game.dealer_has_blackjack is False  # 3 cards

    def test_split_hand_creates_two_hands(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        p.hands[0].hand.cards = [Card("8", 8), Card("8", 8)]
        game.split_hand(p, 0)
        
        assert len(p.hands) == 2
        assert len(p.hands[0].hand.cards) == 2  # Each has 1 original + 1 new
        assert len(p.hands[1].hand.cards) == 2

    def test_split_hand_draws_cards(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        original_hand_count = len(p.hands[0].hand.cards)
        p.hands[0].hand.cards = [Card("8", 8), Card("8", 8)]
        deck_cards_before = len(game.deck.cards)
        
        game.split_hand(p, 0)
        
        # Two cards should be drawn from deck
        assert len(game.deck.cards) == deck_cards_before - 2

    def test_hit_adds_card(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        cards_before = len(p.hands[0].hand.cards)
        game.hit(p, 0)
        
        assert len(p.hands[0].hand.cards) == cards_before + 1

    def test_stand_finishes_hand(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        game.stand(p, 0)
        
        assert p.hands[0].is_finished is True

    def test_double_down(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        original_bet = p.hands[0].bet
        result = game.double(p, 0)
        
        assert p.hands[0].doubled is True
        assert p.hands[0].is_finished is True
        assert p.hands[0].bet == original_bet * 2
        assert result in [TurnResult.DOUBLE, TurnResult.BUST]

    def test_play_dealer_hits_to_17(self):
        players = [("Alice", 10)]
        game = BlackjackGame(players)
        
        game.dealer_hand.cards = [Card("5", 5), Card("2", 2)]
        game.play_dealer()
        
        assert game.dealer_hand.value >= 17 or game.dealer_hand.is_bust

    def test_resolve_insurance(self):
        players = [("Alice", 10), ("Bob", 20)]
        game = BlackjackGame(players)
        
        game.dealer_hand.cards = [Card("Ace", 11), Card("5", 5)]
        game.players[0].insurance_bet = 5
        
        results = game.resolve_insurance()
        assert "Alice" in results
        assert "Bob" in results

    def test_settle_all_bets(self):
        players = [("Alice", 10), ("Bob", 20)]
        game = BlackjackGame(players)
        
        game.stand(game.players[0], 0)
        game.stand(game.players[1], 0)
        game.play_dealer()
        
        results = game.settle_all_bets()
        assert "Alice" in results
        assert "Bob" in results
        
        for name in ["Alice", "Bob"]:
            assert len(results[name]) > 0
            for res in results[name]:
                assert res.result in GameResult
                assert isinstance(res.payout, int)

    def test_full_game_sequence(self):
        players = [("Alice", 50)]
        game = BlackjackGame(players)
        
        p = game.players[0]
        
        # Player hits
        game.hit(p, 0)
        
        # Player stands
        game.stand(p, 0)
        
        # Dealer plays
        game.play_dealer()
        
        # Settle bets
        results = game.settle_all_bets()
        assert "Alice" in results
        assert len(results["Alice"]) > 0
        assert results["Alice"][0].result in GameResult
