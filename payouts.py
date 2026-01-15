from dataclasses import dataclass

from enums import GameResult


@dataclass(frozen=True)
class HandOutcome:
    result: GameResult
    payout: int  # Net payout for the hand (negative for losses)


class PayoutResolver:
    def resolve_hand(self, bet_hand, dealer_hand) -> HandOutcome:
        hand = bet_hand.hand
        bet_amount = bet_hand.bet

        player_blackjack = hand.is_blackjack
        dealer_blackjack = dealer_hand.is_blackjack

        if hand.is_bust:
            return HandOutcome(GameResult.LOSE, -bet_amount)

        if dealer_hand.is_bust:
            return HandOutcome(GameResult.WIN, bet_amount)

        # Natural blackjacks outrank other 21s and pay premium
        if player_blackjack or dealer_blackjack:
            if player_blackjack and dealer_blackjack:
                return HandOutcome(GameResult.PUSH, 0)
            if player_blackjack:
                blackjack_payout = (bet_amount * 3) // 2  # 3:2 payout
                return HandOutcome(GameResult.BLACKJACK_WIN, blackjack_payout)
            return HandOutcome(GameResult.LOSE, -bet_amount)

        if hand.value > dealer_hand.value:
            return HandOutcome(GameResult.WIN, bet_amount)
        if hand.value < dealer_hand.value:
            return HandOutcome(GameResult.LOSE, -bet_amount)
        return HandOutcome(GameResult.PUSH, 0)
