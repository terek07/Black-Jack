# AI Copilot Instructions for Black-Jack

## Architecture Overview

Full-stack blackjack web app with three-tier architecture:

**Frontend (React + Vite)** → **Backend (FastAPI)** → **Game Engine (Python)**

### Frontend Layer ([frontend/src/](../frontend/src/))
- **[App.jsx](../frontend/src/App.jsx)**: Root component managing game session state (`gameId`, `gameState`)
- **[GameSetup.jsx](../frontend/src/components/GameSetup.jsx)**: Player configuration screen (1-4 players, initial bets)
- **[GameBoard.jsx](../frontend/src/components/GameBoard.jsx)**: Main game UI with action buttons, state polling via `fetchGameState()`
- **[Card.jsx](../frontend/src/components/Card.jsx)**: Presentational card component with suit symbols (♠️♥️♣️♦️)
- Communicates with backend via `fetch()` to `http://localhost:8000/api/game/*` endpoints

### Backend Layer ([backend/main.py](../backend/main.py))
- **FastAPI REST API** with in-memory game storage (`games = {}` keyed by UUID)
- Maintains game state between HTTP requests—no websockets, frontend polls for updates
- **Critical transformation layer**: Converts engine's dataclasses to JSON-serializable dicts via `card_to_dict()`, `bet_hand_to_dict()`
- **Dealer card hiding**: `get_game_state()` shows only dealer's first card until game over (`show_dealer_cards` flag)
- CORS enabled for `localhost:5173` (Vite dev server)

### Game Engine Layer ([engine/](../engine/))
- **[game.py](../engine/game.py)**: Main orchestrator (`BlackjackGame`) that coordinates game flow and delegates to specialized managers
- **[models.py](../engine/models.py)**: Core data models (`Card`, `Hand`, `BetHand`, `Player`) using frozen dataclasses for immutability
- **Manager classes**: Each handles a specific game domain:
  - `TurnManager` ([turns.py](../engine/turns.py)): Hit, stand, double operations
  - `SplitManager` ([split.py](../engine/split.py)): Hand splitting logic
  - `InsuranceManager` ([insurance.py](../engine/insurance.py)): Insurance betting
  - `PayoutResolver` ([payouts.py](../engine/payouts.py)): Hand settlement and win/loss/push determination

## Critical Data Flows

### Game Initialization Flow
1. Frontend: User submits player names/bets → `POST /api/game/start`
2. Backend: Creates `BlackjackGame(players)`, stores in `games[uuid]`, calls `game._initial_deal()`
3. Returns `game_id` + initial state (dealer shows 1 card)
4. Frontend polls `GET /api/game/{id}` until `game_over: true`

### Player Action Flow
1. Frontend: Action button → `POST /api/game/{id}/{action}` with `player_index`, `hand_index`
2. Backend: Retrieves game from `games[id]`, calls engine method (e.g., `game.hit()`)
3. Engine: Updates player hand, sets `is_finished` flag, **calls `_advance_turn_if_needed()`**, returns `TurnResult` enum
4. Backend: Returns updated game state with new `current_player_index`; frontend re-renders with next player's buttons

### State Synchronization Pattern
- **No websockets**: Frontend uses `setInterval()` to poll every 500ms during active game
- Backend returns `current_player_index` to highlight active player—buttons only show for active player
- `game_over` flag triggers final state display and stops polling
- Turn advancement is automatic: every action (hit/stand/double) calls `_advance_turn_if_needed()` to move to next player

## Key Design Patterns

### Full-Stack State Management
- **Backend**: In-memory `games` dict (UUID → `BlackjackGame` instance) - state lost on restart
- **Frontend**: Local state (`gameId`, `gameState`) reset on new game via `resetGame()`
- **Engine**: Immutable data models (`Card`, `Hand` frozen dataclasses) prevent accidental mutation

### Hand Tracking & Player Structure
- `Hand` contains cards and computes value dynamically (includes ace-adjustment logic for values > 21)
- `BetHand` wraps a hand with bet amount, `is_finished`, and `doubled` flags
- `Player.hands` is a list to support splits (one player can have multiple concurrent hands)

### Ace Value Adjustment
Critical logic in [models.py](../engine/models.py#L24-L30): aces count as 11 until total exceeds 21, then adjust to 1. Watch for off-by-one issues when testing edge cases like multiple aces.

### Manager Responsibilities
Each manager validates its own preconditions using `ValueError`:
- `SplitManager.split()` raises `ValueError` if cards aren't equal value
- `TurnManager.double()` raises `ValueError` if already doubled or hand isn't 2 cards
- `InsuranceManager.place()` validates bet bounds (0 ≤ amount ≤ bet/2)
- All managers use `can_<action>()` methods for pre-validation checks before calling action methods

### Deck Management
- [Deck](../engine/deck.py) creates and shuffles 52 cards on initialization (4 suits × 13 ranks)
- `deck.draw()` pops from end of list—deck is a **finite resource** that can be exhausted
- In tests, prefer creating `Card` instances directly rather than drawing from shared deck to avoid state coupling

## Testing & Validation

**Run backend server:** `./start-backend.sh` (or `cd backend && uvicorn main:app --reload --port 8000`)

**Run frontend dev server:** `cd frontend && npm run dev` (Vite on port 5173)

**Run all tests:** `pytest` (discovers all `tests/test_*.py` files)

**Run API integration tests:** `pytest tests/test_api.py -v` (requires backend running on port 8000)

**Run specific test file:** `pytest tests/test_game.py` (or test_models.py, test_split.py, etc.)

**Coverage report:** `pytest --cov=. --cov-report=html` generates HTML report in `htmlcov/`

Test organization:
- **Unit tests** organized by component: `test_game.py`, `test_models.py`, `test_turns.py`, `test_split.py`, `test_insurance.py`, `test_payouts.py`
- **API tests** in [test_api.py](../tests/test_api.py): Requires backend running; validates HTTP endpoints and JSON serialization (6 tests)
- **Integration tests** in [test_integration.py](../tests/test_integration.py): Full game flows with edge cases (29 tests covering blackjack scenarios, splits, insurance, dealer behavior, multi-player, complex flows)
- Each test file uses a `TestComponent` class (e.g., `TestBlackjackGame` in [test_game.py](../tests/test_game.py))
- Shared fixtures in [conftest.py](../tests/conftest.py): `fresh_deck`, `single_player`, `blackjack_hand`, `bust_hand`
- Test cards (e.g., `Card("Ace", 11)`) are created directly, not drawn from deck—this avoids deck state issues
- Tests verify both happy paths and constraint violations (e.g., invalid doubles, busts)
- Naming convention: `test_<action>_<expected_behavior>` (e.g., `test_double_multiplies_bet`, `test_split_raises_error_on_invalid_hand`)
- **Current coverage: 100%** across all source modules

## Developer Workflows

### Adding New Game Rules or Mechanics
1. Create data model changes in [models.py](../engine/models.py) if needed (e.g., new flags on `BetHand`)
2. Implement logic in the appropriate manager class (e.g., new action in `TurnManager`)
3. Add the method to `BlackjackGame` delegation layer
4. Write component tests in the corresponding `test_*.py` file
5. Integration test by updating [test_game.py](../tests/test_game.py) full game sequence

### Fixing State Management Issues
- Always check if state is being mutated on immutable objects (`Card`, `Hand`) - create new instances instead
- When modifying player hands through splits, use `player.hands.pop()` and `extend()` not direct assignment
- Validate that `is_finished` flags are set correctly before dealer play

### Adding a New Manager Class
1. Create `manager_name.py` with single responsibility
2. Write unit tests in `test_manager_name.py` using fixtures from [conftest.py](../tests/conftest.py)
3. Integrate into [game.py](../engine/game.py) as a property instantiated in `__init__()`
4. Delegate player/dealer actions through `BlackjackGame` public methods

## Common Operations & Edge Cases

| Operation | File | Notes |
|-----------|------|-------|
| Deal initial cards | `game._initial_deal()` | Loops twice to give 2 cards to each player + dealer |
| Split hand | `game.split_hand()` | Returns tuple of new hands; game replaces player's hand list |
| Dealer auto-play | `TurnManager.dealer_play()` | Hits until value ≥ 17 (no decision-making); **stands on soft 17** |
| Resolve bets | `payouts.resolve_hand()` | Returns enum (WIN/LOSE/PUSH), not payout amounts |
| Blackjack detection | `hand.is_blackjack` | Only true for 2-card 21; beats non-blackjack 21 and pays 3:2 |

### Important Game Rules (as implemented)
- **Soft 17**: Dealer stands on soft 17 (Ace + 6)
- **Blackjack**: Natural blackjack beats non-blackjack 21 and pays 3:2 (push only if dealer also has blackjack)
- **Split**: Creates two new hands with equal bet, each gets one additional card
- **Double**: Multiplies bet, adds one card, immediately ends hand
- **Insurance**: Max bet is half of original bet, pays 2:1 on dealer blackjack

## Integration Points

- `BlackjackGame.__init__()` expects `players: list[tuple[str, int]]` (name, starting bet pairs)
- Deck shuffles on creation; `draw()` pops from end of card list
- Insurance must be resolved before bet settlement (separate calls in game flow)
- Doubled bets are resolved in `PayoutResolver` using the `doubled` flag from `BetHand`

## Conventions

- **Enums** ([enums.py](../engine/enums.py)): Use `TurnResult` for action outcomes, `GameResult` for hand settlement
- **Dataclasses**: `Card` and `Hand` are frozen (immutable); `BetHand`, `Player` are mutable
- **No external dependencies**: Pure Python stdlib only (dataclasses, enum, random)
