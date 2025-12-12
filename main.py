import random

DECK = [
    ("Ace of Hearts", 11), ("2 of Hearts", 2), ("3 of Hearts", 3), ("4 of Hearts", 4),
    ("5 of Hearts", 5), ("6 of Hearts", 6), ("7 of Hearts", 7), ("8 of Hearts", 8),
    ("9 of Hearts", 9), ("10 of Hearts", 10), ("Jack of Hearts", 10),
    ("Queen of Hearts", 10), ("King of Hearts", 10),

    ("Ace of Diamonds", 11), ("2 of Diamonds", 2), ("3 of Diamonds", 3),
    ("4 of Diamonds", 4), ("5 of Diamonds", 5), ("6 of Diamonds", 6),
    ("7 of Diamonds", 7), ("8 of Diamonds", 8), ("9 of Diamonds", 9),
    ("10 of Diamonds", 10), ("Jack of Diamonds", 10),
    ("Queen of Diamonds", 10), ("King of Diamonds", 10),

    ("Ace of Clubs", 11), ("2 of Clubs", 2), ("3 of Clubs", 3),
    ("4 of Clubs", 4), ("5 of Clubs", 5), ("6 of Clubs", 6),
    ("7 of Clubs", 7), ("8 of Clubs", 8), ("9 of Clubs", 9),
    ("10 of Clubs", 10), ("Jack of Clubs", 10),
    ("Queen of Clubs", 10), ("King of Clubs", 10),

    ("Ace of Spades", 11), ("2 of Spades", 2), ("3 of Spades", 3),
    ("4 of Spades", 4), ("5 of Spades", 5), ("6 of Spades", 6),
    ("7 of Spades", 7), ("8 of Spades", 8), ("9 of Spades", 9),
    ("10 of Spades", 10), ("Jack of Spades", 10),
    ("Queen of Spades", 10), ("King of Spades", 10)
]


used_carts = set()

players = []
dealer_hand = []

def random_card():
    id = random.randrange(0, 52)
    if id in used_carts:
        return random_card()
    else:
        used_carts.add(id)
        return DECK[id]
        
def display_hand(hand, dealer=False):
    if dealer:
        print("Dealer: ")
        print(hand[0][0])
        return None
    value = 0
    for card in hand:
        print(card[0])
        value += card[1]
    print("Value: ", value)
    return value
    
def start_game():
    players_amount = int(input("How many players? "))
    for _ in range(players_amount):# deal starting hand
        players.append([random_card(), random_card()])
    dealer_hand = [random_card(), random_card()]   
    print("Dealer's hand: ")
    display_hand(dealer_hand, True)
    for i in range(0, players_amount):
        print("Player ", i + 1)
        print("Your hand: ")
        if display_hand(players[i]) == 21:
            print("It's black jack! You won!")
            continue
        
        while(True):
            action = input("Your action(h - hit, s - stand): ")
            if action == 's':
                break
            if action == 'h':
                next_card = random_card()
                print("New card: ", next_card[0])
                players[i].append(next_card)
                if display_hand(players[i]) > 21:
                    print("You Busted!")
                    break
            else:
                print("Error")
        
        
start_game()
    
    
