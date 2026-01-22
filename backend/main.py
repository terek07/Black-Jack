from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import threading
import copy

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.game import BlackjackGame
from engine.models import Card, BetHand
from engine.enums import GameResult

app = FastAPI(title="Blackjack Game API")

# Add CORS middleware FIRST with wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

games = {}
# Cache resolve responses to make /resolve idempotent (avoid double-applying payouts)
_resolve_response_cache = {}
# Per-game locks to avoid concurrent resolve executions
_resolve_locks = {}

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
    suits = ['Hearts','Diamonds','Clubs' ,'Spades']

    for suit_name in suits:
        if suit_name in card.name:
            return {"suit": suit_name, "value": card.value}

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
    
    players_data = [{
            "name": player.name,
            "balance": player.balance,
            "hands": [bet_hand_to_dict(bh) for bh in player.hands],
            "insurance_bet": player.insurance_bet
        } for player in game.players]
    
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

    # Fast path: return cached response if already resolved
    cached = _resolve_response_cache.get(game_id)
    if cached is not None:
        return copy.deepcopy(cached)

    # Ensure a lock exists for this game
    lock = _resolve_locks.setdefault(game_id, threading.Lock())

    # Acquire lock to perform resolve exactly once
    acquired = lock.acquire(timeout=5.0)
    if not acquired:
        # If we couldn't acquire lock in reasonable time, try returning cached response
        cached = _resolve_response_cache.get(game_id)
        if cached is not None:
            return copy.deepcopy(cached)
        raise HTTPException(status_code=503, detail="Resolve in progress, try again")

    try:
        # Another thread may have resolved while we waited for lock — check again
        cached = _resolve_response_cache.get(game_id)
        if cached is not None:
            return copy.deepcopy(cached)

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

        # Cache a deep copy and return a deep copy
        _resolve_response_cache[game_id] = copy.deepcopy(response_dict)
        return copy.deepcopy(response_dict)
    finally:
        lock.release()

@app.get("/api/game/{game_id}")
async def get_game(game_id: str):
    return get_game_state(game_id)

@app.get("/health")
async def health():
    return {"status": "ok", "cors_origins": cors_origins}

@app.get("/debug/cors")
async def debug_cors():
    return {"allowed_origins": cors_origins, "env_cors_origins": os.getenv("CORS_ORIGINS", "not set")}
#refres