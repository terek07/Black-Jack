from typing import List
from models import Deck, Player
from enums import TurnResult, GameResult


class BlackjackGame:
    def __init__(self, players: List[Player]):
        self.deck = Deck()
        self.players = players
        self.dealer = Player("Dealer")
        self._initial_deal()

    def _initial_deal(self):
        for _ in range(2):
            for player in self.players:
                player.hand.add_card(self.deck.draw())
            self.dealer.hand.add_card(self.deck.draw())

    def hit(self, player: Player) -> TurnResult:
        player.hand.add_card(self.deck.draw())

        if player.hand.is_blackjack:
            return TurnResult.BLACKJACK
        if player.hand.is_bust:
            return TurnResult.BUST
        return TurnResult.CONTINUE

    def stand(self, player: Player) -> TurnResult:
        return TurnResult.STAND

    def dealer_play(self):
        while self.dealer.hand.value < 17:
            self.dealer.hand.add_card(self.deck.draw())

    def settle_bet(self, player: Player) -> GameResult:
        player_value = player.hand.value
        dealer_value = self.dealer.hand.value

        if player.hand.is_bust:
            return GameResult.LOSE
        if self.dealer.hand.is_bust:
            return GameResult.WIN
        if player_value > dealer_value:
            return GameResult.WIN
        if player_value < dealer_value:
            return GameResult.LOSE
        return GameResult.PUSH
