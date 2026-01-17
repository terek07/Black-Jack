from engine.models import BetHand, Hand


class SplitManager:
    def can_split(self, bet_hand: BetHand) -> bool:
        cards = bet_hand.hand.cards
        return len(cards) == 2 and cards[0].value == cards[1].value

    def split(self, bet_hand: BetHand) -> tuple[BetHand, BetHand]:
        if not self.can_split(bet_hand):
            raise ValueError("Hand cannot be split")

        c1, c2 = bet_hand.hand.cards

        h1 = BetHand(hand=Hand(cards=[c1]), bet=bet_hand.bet)
        h2 = BetHand(hand=Hand(cards=[c2]), bet=bet_hand.bet)

        return h1, h2
