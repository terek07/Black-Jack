from deck import Deck
from models import Player, BetHand
from insurance import InsuranceManager
from split import SplitManager
from turns import TurnManager
from payouts import PayoutResolver


class BlackjackGame:
    def __init__(self, players: list[Player]):
        self.deck = Deck()
        self.players = players
        self.dealer = Player("Dealer")

        self.insurance = InsuranceManager()
        self.split = SplitManager()
        self.turns = TurnManager()
        self.payouts = PayoutResolver()

        self._initial_deal()

    def _initial_deal(self):
        for p in self.players:
            bet_hand = BetHand(bet=bet_hand.bet if hasattr(p, "bet_hand") else 0)
            bet_hand.hand.add(self.deck.draw())
            bet_hand.hand.add(self.deck.draw())
            p.hands.append(bet_hand)

        self.dealer.hands = []
        self.dealer_hand = BetHand()
        self.dealer_hand.hand.add(self.deck.draw())
        self.dealer_hand.hand.add(self.deck.draw())
        self.dealer.hand = self.dealer_hand.hand

    @property
    def dealer_has_blackjack(self) -> bool:
        return self.dealer.hand.is_blackjack

    def split_hand(self, player: Player, hand_index: int):
        bet_hand = player.hands[hand_index]

        if not self.split.can_split(bet_hand):
            raise ValueError("Cannot split this hand")

        h1, h2 = self.split.split(bet_hand)

        h1.hand.add(self.deck.draw())
        h2.hand.add(self.deck.draw())

        player.hands.pop(hand_index)
        player.hands.extend([h1, h2])

    def play_dealer(self):
        self.turns.dealer_play(self.dealer, self.deck)

    def resolve_insurance(self) -> dict:
        return {
            p.name: self.insurance.resolve(p, self.dealer_has_blackjack)
            for p in self.players
        }

    def settle_all_bets(self) -> dict:
        results = {}
        for p in self.players:
            results[p.name] = []
            for hand in p.hands:
                results[p.name].append(
                    self.payouts.resolve_hand(hand, self.dealer)
                )
        return results
