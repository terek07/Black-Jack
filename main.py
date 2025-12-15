import random


class Card:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Deck:
    def __init__(self):
        self.cards = [
            Card("Ace of Hearts", 11), Card("2 of Hearts", 2), Card("3 of Hearts", 3),
            Card("4 of Hearts", 4), Card("5 of Hearts", 5), Card("6 of Hearts", 6),
            Card("7 of Hearts", 7), Card("8 of Hearts", 8), Card("9 of Hearts", 9),
            Card("10 of Hearts", 10), Card("Jack of Hearts", 10),
            Card("Queen of Hearts", 10), Card("King of Hearts", 10),

            Card("Ace of Diamonds", 11), Card("2 of Diamonds", 2), Card("3 of Diamonds", 3),
            Card("4 of Diamonds", 4), Card("5 of Diamonds", 5), Card("6 of Diamonds", 6),
            Card("7 of Diamonds", 7), Card("8 of Diamonds", 8), Card("9 of Diamonds", 9),
            Card("10 of Diamonds", 10), Card("Jack of Diamonds", 10),
            Card("Queen of Diamonds", 10), Card("King of Diamonds", 10),

            Card("Ace of Clubs", 11), Card("2 of Clubs", 2), Card("3 of Clubs", 3),
            Card("4 of Clubs", 4), Card("5 of Clubs", 5), Card("6 of Clubs", 6),
            Card("7 of Clubs", 7), Card("8 of Clubs", 8), Card("9 of Clubs", 9),
            Card("10 of Clubs", 10), Card("Jack of Clubs", 10),
            Card("Queen of Clubs", 10), Card("King of Clubs", 10),

            Card("Ace of Spades", 11), Card("2 of Spades", 2), Card("3 of Spades", 3),
            Card("4 of Spades", 4), Card("5 of Spades", 5), Card("6 of Spades", 6),
            Card("7 of Spades", 7), Card("8 of Spades", 8), Card("9 of Spades", 9),
            Card("10 of Spades", 10), Card("Jack of Spades", 10),
            Card("Queen of Spades", 10), Card("King of Spades", 10)
        ]
        self.used_cards = set()

    def draw_card(self):
        while True:
            card_id = random.randrange(0, len(self.cards))
            if card_id not in self.used_cards:
                self.used_cards.add(card_id)
                return self.cards[card_id]


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bet = 0

    def display_hand(self, dealer=False):
        if dealer:
            print(self.hand[0].name)
            return None

        hand_value = 0
        aces = 0
        for card in self.hand:
            print(card.name)
            card_value = card.value
            if card_value == 11:
                aces += 1
            while hand_value + card_value > 21:
                if aces:
                    hand_value -= 10
                    aces -= 1
                else:
                    break
            hand_value += card_value
        print("Value: ", hand_value)
        return hand_value


class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.players = []
        self.dealer = Player("Dealer")

    def starting_bets(self):
        print("Choose starting bets: ")
        for player in self.players:
            player.bet = int(input(f"{player.name}, enter your bet: "))

    def deal_cards(self):
        num_players = int(input("How many players? "))
        for i in range(num_players):
            player_name = f"Player {i + 1}"
            player = Player(player_name)
            player.hand = [self.deck.draw_card(), self.deck.draw_card()]
            self.players.append(player)
        self.dealer.hand = [self.deck.draw_card(), self.deck.draw_card()]
    def turn(self, player):
        print(f"{player.name}'s turn")
        print("Your hand: ")
        if player.display_hand() == 21:
            print("It's blackjack! You won!")
            return

        while True:
            action = input("Your action (h - hit, s - stand): ")
            if action == 's':
                return
            elif action == 'h':
                next_card = self.deck.draw_card()
                print("New card: ", next_card.name)
                player.hand.append(next_card)
                if player.display_hand() > 21:
                    print("You Busted!")
                    return
            else:
                print("Invalid action. Please choose 'h' or 's'.")

    def start_game(self):

        self.deal_cards()
        self.starting_bets()

        print("Dealer's hand: ")
        self.dealer.display_hand(dealer=True)

        for player in self.players:
            self.turn(player)


if __name__ == "__main__":
    game = BlackjackGame()
    game.start_game()