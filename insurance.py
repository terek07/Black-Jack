from models import Player


class InsuranceManager:
    def is_available(self, dealer_hand) -> bool:
        return dealer_hand.cards[0].value == 11

    def place(self, player: Player, amount: int):
        if amount < 0 or amount > player.hands[0].bet / 2:
            raise ValueError("Invalid insurance amount")
        player.insurance_bet = amount

    def resolve(self, player: Player, dealer_has_blackjack: bool) -> int:
        if player.insurance_bet == 0:
            return 0
        return (
            player.insurance_bet * 2
            if dealer_has_blackjack
            else -player.insurance_bet
        )
