from deck import Deck
from models import Player, BetHand, Hand
from insurance import InsuranceManager
from split import SplitManager
from turns import TurnManager
from payouts import PayoutResolver


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

        self._initial_deal()

    def _initial_deal(self):
        for _ in range(2):
            for p in self.players:
                p.hands[0].hand.add(self.deck.draw())
            self.dealer_hand.add(self.deck.draw())

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
        return self.turns.hit(player.hands[hand_index], self.deck)

    def stand(self, player: Player, hand_index: int):
        return self.turns.stand(player.hands[hand_index])

    def double(self, player: Player, hand_index: int):
        return self.turns.double(player.hands[hand_index], self.deck)

    def play_dealer(self):
        self.turns.dealer_play(self.dealer_hand, self.deck)

    def resolve_insurance(self) -> dict:
        return {
            p.name: self.insurance.resolve(p, self.dealer_has_blackjack)
            for p in self.players
        }

    def resolve_bets(self):
        results = []
        for p in self.players:
            player_results = []
            for hand in p.hands:
                outcome = self.payouts.resolve_hand(hand, self.dealer_hand)
                player_results.append(outcome.result)
                
                from enums import GameResult
                if outcome.result in (GameResult.WIN, GameResult.BLACKJACK_WIN):
                    payout = hand.bet * 2
                    if hand.hand.is_blackjack:
                        payout = int(hand.bet * 2.5)
                    p.balance += payout
                elif outcome.result == GameResult.PUSH:
                    p.balance += hand.bet
            
            results.append(player_results)
        return results

    def place_insurance(self, player: Player, amount: int):
        return self.insurance.place(player, amount)

    def settle_all_bets(self) -> dict:
        results = {}
        for p in self.players:
            results[p.name] = []
            for hand in p.hands:
                results[p.name].append(
                    self.payouts.resolve_hand(hand, self.dealer_hand)
                )
        return results
