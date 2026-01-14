from enums import TurnResult


class TurnManager:
    def hit(self, bet_hand, deck):
        bet_hand.hand.add(deck.draw())

        if bet_hand.hand.is_bust:
            bet_hand.is_finished = True
            return TurnResult.BUST

        return TurnResult.CONTINUE

    def stand(self, bet_hand):
        bet_hand.is_finished = True
        return TurnResult.STAND

    def can_double(self, bet_hand) -> bool:
        return (
            len(bet_hand.hand.cards) == 2
            and not bet_hand.doubled
        )

    def double(self, bet_hand, deck):
        if not self.can_double(bet_hand):
            raise ValueError("Cannot double this hand")

        bet_hand.bet *= 2
        bet_hand.doubled = True

        bet_hand.hand.add(deck.draw())
        bet_hand.is_finished = True

        if bet_hand.hand.is_bust:
            return TurnResult.BUST

        return TurnResult.DOUBLE

    def dealer_play(self, dealer_hand, deck):
        while dealer_hand.value < 17:
            dealer_hand.add(deck.draw())
