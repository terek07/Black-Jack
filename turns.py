from enums import TurnResult


class TurnManager:
    def hit(self, bet_hand, deck):
        bet_hand.hand.add(deck.draw())

        if bet_hand.hand.is_blackjack:
            bet_hand.is_finished = True
            return TurnResult.BLACKJACK

        if bet_hand.hand.is_bust:
            bet_hand.is_finished = True
            return TurnResult.BUST

        return TurnResult.CONTINUE

    def stand(self, bet_hand):
        bet_hand.is_finished = True
        return TurnResult.STAND

    def dealer_play(self, dealer, deck):
        while dealer.hand.value < 17:
            dealer.hand.add(deck.draw())
