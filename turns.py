from enums import TurnResult


class TurnManager:
    def hit(self, player, deck):
        player.hand.add(deck.draw())
        if player.hand.is_blackjack:
            return TurnResult.BLACKJACK
        if player.hand.is_bust:
            return TurnResult.BUST
        return TurnResult.CONTINUE

    def stand(self):
        return TurnResult.STAND

    def dealer_play(self, dealer, deck):
        while dealer.hand.value < 17:
            dealer.hand.add(deck.draw())
