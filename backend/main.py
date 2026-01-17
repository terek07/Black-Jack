from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import BlackjackGame
from engine.models import Card, BetHand
from engine.enums import GameResult

app = FastAPI(title="Blackjack Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}

class PlayerInput(BaseModel):
    name: str
    bet: int

class StartGameRequest(BaseModel):
    players: List[PlayerInput]

class ActionRequest(BaseModel):
    game_id: str
    player_index: int
    hand_index: int = 0

class InsuranceRequest(BaseModel):
    game_id: str
    player_index: int
    amount: int

class GameStateResponse(BaseModel):
    game_id: str
    players: List[dict]
    dealer_hand: List[dict]
    dealer_value: int
    current_player_index: Optional[int]
    game_over: bool

def card_to_dict(card: Card):
    suit_map = {
        'Hearts': 'Hearts',
        'Diamonds': 'Diamonds',
        'Clubs': 'Clubs',
        'Spades': 'Spades'
    }
    
    for suit_name in suit_map:
        if suit_name in card.name:
            return {"suit": suit_name, "value": card.value}
    
    return {"suit": card.name, "value": card.value}

def hand_to_dict(hand):
    return {
        "cards": [card_to_dict(card) for card in hand.cards],
        "value": hand.value,
        "is_blackjack": hand.is_blackjack,
        "is_bust": hand.is_bust
    }

def bet_hand_to_dict(bet_hand: BetHand):
    return {
        "bet": bet_hand.bet,
        "doubled": bet_hand.doubled,
        "is_finished": bet_hand.is_finished,
        **hand_to_dict(bet_hand.hand)
    }

def get_game_state(game_id: str, show_dealer_cards: bool = False):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    dealer_cards = game.dealer_hand.cards if show_dealer_cards else [game.dealer_hand.cards[0]]
    dealer_value = game.dealer_hand.value if show_dealer_cards else game.dealer_hand.cards[0].value
    
    players_data = []
    for player in game.players:
        player_data = {
            "name": player.name,
            "balance": player.balance,
            "hands": [bet_hand_to_dict(bh) for bh in player.hands],
            "insurance_bet": player.insurance_bet
        }
        players_data.append(player_data)
    
    all_finished = all(
        all(bh.is_finished for bh in player.hands)
        for player in game.players
    )
    
    return GameStateResponse(
        game_id=game_id,
        players=players_data,
        dealer_hand=[card_to_dict(card) for card in dealer_cards],
        dealer_value=dealer_value,
        current_player_index=game.current_player_index,
        game_over=all_finished
    )

@app.post("/api/game/start")
async def start_game(request: StartGameRequest):
    import uuid
    game_id = str(uuid.uuid4())
    
    players = [(p.name, p.bet) for p in request.players]
    game = BlackjackGame(players)
    games[game_id] = game
    
    return get_game_state(game_id)

@app.post("/api/game/{game_id}/hit")
async def hit(request: ActionRequest):
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[request.game_id]
    player = game.players[request.player_index]
    
    try:
        game.hit(player, request.hand_index)
        return get_game_state(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/game/{game_id}/stand")
async def stand(request: ActionRequest):
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[request.game_id]
    player = game.players[request.player_index]
    
    try:
        game.stand(player, request.hand_index)
        
        all_finished = all(
            all(bh.is_finished for bh in p.hands)
            for p in game.players
        )
        
        show_dealer = all_finished
        return get_game_state(request.game_id, show_dealer_cards=show_dealer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/game/{game_id}/double")
async def double(request: ActionRequest):
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[request.game_id]
    player = game.players[request.player_index]
    
    try:
        game.double(player, request.hand_index)
        return get_game_state(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/game/{game_id}/split")
async def split(request: ActionRequest):
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[request.game_id]
    player = game.players[request.player_index]
    
    try:
        game.split_hand(player, request.hand_index)
        return get_game_state(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/game/{game_id}/insurance")
async def place_insurance(request: InsuranceRequest):
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[request.game_id]
    player = game.players[request.player_index]
    
    try:
        game.place_insurance(player, request.amount)
        return get_game_state(request.game_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/game/{game_id}/resolve")
async def resolve_game(game_id: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    game.play_dealer()
    insurance_results = game.resolve_insurance()
    results = game.resolve_bets()
    
    response = get_game_state(game_id, show_dealer_cards=True)
    response_dict = response.dict()
    response_dict["results"] = [
        {
            "player_name": player.name,
            "final_balance": player.balance,
            "insurance_payout": insurance_results.get(player.name, 0),
            "total_payout": sum(r.payout for r in player_results) + insurance_results.get(player.name, 0),
            "hand_results": [
                {
                    "hand_index": idx,
                    "result": r.result.value,
                    "payout": r.payout,
                    "bet": hand.bet,
                    "hand_value": hand.hand.value,
                    "is_blackjack": hand.hand.is_blackjack,
                    "is_bust": hand.hand.is_bust,
                }
                for idx, (r, hand) in enumerate(zip(player_results, player.hands))
            ],
        }
        for player, player_results in zip(game.players, results)
    ]
    
    return response_dict

@app.get("/api/game/{game_id}")
async def get_game(game_id: str):
    return get_game_state(game_id)

@app.get("/health")
async def health():
    return {"status": "ok"}
