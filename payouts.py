from enums import GameResult


class PayoutResolver:
    def resolve_main(self, player, dealer) -> GameResult:
        if player.hand.is_bust:
            return GameResult.LOSE
        if dealer.hand.is_bust:
            return GameResult.WIN
        if player.hand.value > dealer.hand.value:
            return GameResult.WIN
        if player.hand.value < dealer.hand.value:
            return GameResult.LOSE
        return GameResult.PUSH
