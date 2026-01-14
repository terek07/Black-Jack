import pytest
from models import Card, BetHand, Hand
from turns import TurnManager
from enums import TurnResult


class TestTurnManager:
    def test_hit_continues_game(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        result = tm.hit(hand, fresh_deck)
        assert result in [TurnResult.CONTINUE, TurnResult.BUST]
        assert len(hand.hand.cards) == 3  # Initial 2 + 1 hit

    def test_hit_bust_ends_hand(self, fresh_deck):
        tm = TurnManager()
        hand = BetHand()
        hand.hand.add(Card("10", 10))
        hand.hand.add(Card("10", 10))
        result = tm.hit(hand, fresh_deck)
        assert result == TurnResult.BUST
        assert hand.is_finished is True

    def test_stand_ends_hand(self, single_player):
        tm = TurnManager()
        hand = single_player.hands[0]
        result = tm.stand(hand)
        assert result == TurnResult.STAND
        assert hand.is_finished is True

    def test_can_double_on_initial_hand(self, single_player):
        tm = TurnManager()
        hand = single_player.hands[0]
        assert tm.can_double(hand) is True

    def test_cannot_double_with_three_cards(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        tm.hit(hand, fresh_deck)  # Now has 3 cards
        assert tm.can_double(hand) is False

    def test_cannot_double_already_doubled(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        tm.double(hand, fresh_deck)
        assert hand.doubled is True
        with pytest.raises(ValueError):
            tm.double(hand, fresh_deck)

    def test_double_multiplies_bet(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        original_bet = hand.bet
        tm.double(hand, fresh_deck)
        assert hand.bet == original_bet * 2

    def test_double_adds_one_card(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        cards_before = len(hand.hand.cards)
        tm.double(hand, fresh_deck)
        assert len(hand.hand.cards) == cards_before + 1

    def test_double_ends_hand(self, single_player, fresh_deck):
        tm = TurnManager()
        hand = single_player.hands[0]
        result = tm.double(hand, fresh_deck)
        assert hand.is_finished is True
        assert result in [TurnResult.DOUBLE, TurnResult.BUST]

    def test_double_without_bust(self):
        tm = TurnManager()
        hand = BetHand()
        hand.hand.add(Card("5", 5))
        hand.hand.add(Card("4", 4))
        # Hand value: 9, doubling should not bust with any card
        
        from deck import Deck
        deck = Deck()
        result = tm.double(hand, deck)
        # Result should be DOUBLE (not BUST) since max we can get is 9 + 10 = 19
        assert result == TurnResult.DOUBLE

    def test_dealer_play_hits_until_17(self):
        tm = TurnManager()
        dealer_hand = Hand()
        dealer_hand.add(Card("5", 5))
        dealer_hand.add(Card("2", 2))
        # Dealer hand value is 7, should continue hitting
        
        from deck import Deck
        deck = Deck()
        cards_before = len(deck.cards)
        tm.dealer_play(dealer_hand, deck)
        
        assert dealer_hand.value >= 17 or dealer_hand.is_bust
        assert len(deck.cards) < cards_before  # Cards were drawn

    def test_dealer_play_stops_at_17(self):
        tm = TurnManager()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("7", 7))
        # Dealer hand value is 17, should stop
        
        from deck import Deck
        deck = Deck()
        cards_before = len(deck.cards)
        tm.dealer_play(dealer_hand, deck)
        
        assert dealer_hand.value == 17
