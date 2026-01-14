from models import Player


class InsuranceManager:
    def is_available(self, dealer) -> bool:
        return dealer.hand.cards[0].value == 11  # Ace showing

    def place(self, player: Player, amount: int):
        if amount < 0 or amount > player.hands[0].bet / 2:
            raise ValueError("Invalid insurance amount")
        player.insurance_bet = amount

    def resolve(self, player: Player, dealer_has_blackjack: bool) -> int:
        if player.insurance_bet == 0:
            return 0

        if dealer_has_blackjack:
            return player.insurance_bet * 2
        return -player.insurance_bet
