from deck import Deck
from models import Player
from insurance import InsuranceManager
from turns import TurnManager
from payouts import PayoutResolver


class BlackjackGame:
    def __init__(self, players: list[Player]):
        self.deck = Deck()
        self.players = players
        self.dealer = Player("Dealer")

        self.turns = TurnManager()
        self.insurance = InsuranceManager()
        self.payouts = PayoutResolver()

        self._initial_deal()

    def _initial_deal(self):
        for _ in range(2):
            for p in self.players:
                p.hand.add(self.deck.draw())
            self.dealer.hand.add(self.deck.draw())

    @property
    def dealer_has_blackjack(self) -> bool:
        return self.dealer.hand.is_blackjack

    def resolve_insurance(self) -> dict:
        results = {}
        for p in self.players:
            results[p.name] = self.insurance.resolve(
                p, self.dealer_has_blackjack
            )
        return results

    def play_dealer(self):
        self.turns.dealer_play(self.dealer, self.deck)

    def settle_main_bets(self) -> dict:
        return {
            p.name: self.payouts.resolve_main(p, self.dealer)
            for p in self.players
        }
