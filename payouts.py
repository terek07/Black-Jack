from enums import GameResult


class PayoutResolver:
    def resolve_hand(self, bet_hand, dealer_hand) -> GameResult:
        hand = bet_hand.hand

        if hand.is_bust:
            return GameResult.LOSE
        if dealer_hand.is_bust:
            return GameResult.WIN
        if hand.value > dealer_hand.value:
            return GameResult.WIN
        if hand.value < dealer_hand.value:
            return GameResult.LOSE
        return GameResult.PUSH
