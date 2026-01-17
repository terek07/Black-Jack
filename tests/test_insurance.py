import pytest
from engine.models import Card, Hand
from engine.insurance import InsuranceManager


class TestInsuranceManager:
    def test_is_available_with_ace(self):
        im = InsuranceManager()
        dealer_hand = Hand()
        dealer_hand.add(Card("Ace of Spades", 11))
        dealer_hand.add(Card("5 of Hearts", 5))
        assert im.is_available(dealer_hand) is True

    def test_is_not_available_without_ace(self):
        im = InsuranceManager()
        dealer_hand = Hand()
        dealer_hand.add(Card("10", 10))
        dealer_hand.add(Card("5", 5))
        assert im.is_available(dealer_hand) is False

    def test_place_insurance_valid(self, single_player):
        im = InsuranceManager()
        im.place(single_player, 5)
        assert single_player.insurance_bet == 5

    def test_place_insurance_zero(self, single_player):
        im = InsuranceManager()
        im.place(single_player, 0)
        assert single_player.insurance_bet == 0

    def test_place_insurance_max_half_of_bet(self, single_player):
        # single_player has bet of 10, max insurance is 5
        im = InsuranceManager()
        im.place(single_player, 5)
        assert single_player.insurance_bet == 5

    def test_place_insurance_exceeds_max(self, single_player):
        im = InsuranceManager()
        # single_player has bet of 10, max insurance is 5
        with pytest.raises(ValueError):
            im.place(single_player, 6)

    def test_place_insurance_negative(self, single_player):
        im = InsuranceManager()
        with pytest.raises(ValueError):
            im.place(single_player, -1)

    def test_resolve_insurance_win(self, single_player):
        im = InsuranceManager()
        single_player.insurance_bet = 5
        payout = im.resolve(single_player, dealer_has_blackjack=True)
        assert payout == 10  # 2x bet

    def test_resolve_insurance_lose(self, single_player):
        im = InsuranceManager()
        single_player.insurance_bet = 5
        payout = im.resolve(single_player, dealer_has_blackjack=False)
        assert payout == -5

    def test_resolve_insurance_no_bet(self, single_player):
        im = InsuranceManager()
        single_player.insurance_bet = 0
        payout = im.resolve(single_player, dealer_has_blackjack=True)
        assert payout == 0  # No bet, no payout
