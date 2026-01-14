from enums import GameResult


class PayoutResolver:
    def resolve_hand(self, bet_hand, dealer) -> GameResult:
        hand = bet_hand.hand

        if hand.is_bust:
            return GameResult.LOSE
        if dealer.hand.is_bust:
            return GameResult.WIN
        if hand.value > dealer.hand.value:
            return GameResult.WIN
        if hand.value < dealer.hand.value:
            return GameResult.LOSE
        return GameResult.PUSH
