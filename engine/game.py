from engine.deck import Deck
from engine.models import Player, BetHand, Hand, Card
from engine.insurance import InsuranceManager
from engine.split import SplitManager
from engine.turns import TurnManager
from engine.payouts import PayoutResolver


class BlackjackGame:
    def __init__(self, players: list[tuple[str, int]]):
        """
        players: [(name, starting_bet)]
        """
        self.deck = Deck()
        self.players = []
        self.dealer_hand = Hand()
        self.current_player_index = 0

        self.insurance = InsuranceManager()
        self.split = SplitManager()
        self.turns = TurnManager()
        self.payouts = PayoutResolver()

        for name, bet in players:
            p = Player(name)
            bh = BetHand(bet=bet)
            p.hands.append(bh)
            self.players.append(p)

        # self._test_initial_deal()
        self._initial_deal()
        self._auto_finish_natural_blackjacks()
        self._advance_turn_if_needed()

    def _initial_deal(self):
        for _ in range(2):
            for p in self.players:
                p.hands[0].hand.add(self.deck.draw())
            self.dealer_hand.add(self.deck.draw())

    # to showcase insurance without waiting for black  jack
    def _test_initial_deal(self):
        for _ in range(2):
            for p in self.players:
                p.hands[0].hand.add(self.deck.draw())
        self.dealer_hand.add(Card("Ace of Spades", 11))
        self.dealer_hand.add(Card("10 of Spades", 10))

    def _advance_turn_if_needed(self):
        if self.current_player_index is None:
            return

        while self.current_player_index < len(self.players):
            current_player = self.players[self.current_player_index]
            if any(not hand.is_finished for hand in current_player.hands):
                return
            self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.current_player_index = None

    def _auto_finish_natural_blackjacks(self):
        for player in self.players:
            for bet_hand in player.hands:
                if bet_hand.hand.is_blackjack:
                    bet_hand.is_finished = True

    @property
    def dealer_has_blackjack(self) -> bool:
        return self.dealer_hand.is_blackjack

    def split_hand(self, player: Player, hand_index: int):
        bet_hand = player.hands[hand_index]

        h1, h2 = self.split.split(bet_hand)
        h1.hand.add(self.deck.draw())
        h2.hand.add(self.deck.draw())

        player.hands.pop(hand_index)
        player.hands.extend([h1, h2])

    def hit(self, player: Player, hand_index: int):
        result = self.turns.hit(player.hands[hand_index], self.deck)
        self._advance_turn_if_needed()
        return result

    def stand(self, player: Player, hand_index: int):
        result = self.turns.stand(player.hands[hand_index])
        self._advance_turn_if_needed()
        return result

    def double(self, player: Player, hand_index: int):
        result = self.turns.double(player.hands[hand_index], self.deck)
        self._advance_turn_if_needed()
        return result

    def play_dealer(self):
        # Delegate to TurnManager to perform dealer auto-play (hit until 17)
        self.turns.dealer_play(self.dealer_hand, self.deck)

    def resolve_insurance(self) -> dict:
        results = {}
        for p in self.players:
            payout = self.insurance.resolve(p, self.dealer_has_blackjack)
            p.balance += payout
            results[p.name] = payout
        return results

    def resolve_bets(self):
        results = []
        for p in self.players:
            player_results = []
            for hand in p.hands:
                outcome = self.payouts.resolve_hand(hand, self.dealer_hand)
                p.balance += outcome.payout
                player_results.append(outcome)
            results.append(player_results)
        return results

    def place_insurance(self, player: Player, amount: int):
        return self.insurance.place(player, amount)
