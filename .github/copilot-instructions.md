# AI Copilot Instructions for Black-Jack

## Architecture Overview

This is a modular blackjack game engine with a clean separation of concerns:

- **[game.py](../game.py)**: Main orchestrator (`BlackjackGame`) that coordinates game flow and delegates to specialized managers
- **[models.py](../models.py)**: Core data models (`Card`, `Hand`, `BetHand`, `Player`) using frozen dataclasses for immutability
- **Manager classes**: Each handles a specific game domain:
  - `TurnManager` ([turns.py](../turns.py)): Hit, stand, double operations
  - `SplitManager` ([split.py](../split.py)): Hand splitting logic
  - `InsuranceManager` ([insurance.py](../insurance.py)): Insurance betting
  - `PayoutResolver` ([payouts.py](../payouts.py)): Hand settlement and win/loss/push determination

## Key Design Patterns

### State Management in Hand Tracking
- `Hand` contains cards and computes value dynamically (includes ace-adjustment logic for values > 21)
- `BetHand` wraps a hand with bet amount, `is_finished`, and `doubled` flags
- `Player.hands` is a list to support splits (one player can have multiple concurrent hands)

### Ace Value Adjustment
Critical logic in [models.py](../models.py#L24-L30): aces count as 11 until total exceeds 21, then adjust to 1. Watch for off-by-one issues when testing edge cases like multiple aces.

### Manager Responsibilities
Each manager validates its own preconditions:
- `SplitManager.split()` raises `ValueError` if cards aren't equal value
- `TurnManager.double()` raises `ValueError` if already doubled or hand isn't 2 cards
- `InsuranceManager.place()` validates bet bounds

## Testing & Validation

Run tests: `pytest test_blackjack.py`

Test organization in [test_blackjack.py](../test_blackjack.py):
- Uses pytest fixtures for reusable game components (`fresh_deck`, `single_player`, hands with known card combinations)
- Test cards (e.g., `Card("Ace", 11)`) are created directly, not drawn from deck—this avoids deck state issues
- Tests verify both happy paths and constraint violations (e.g., invalid doubles, busts)

## Common Operations & Edge Cases

| Operation | File | Notes |
|-----------|------|-------|
| Deal initial cards | `game._initial_deal()` | Loops twice to give 2 cards to each player + dealer |
| Split hand | `game.split_hand()` | Returns tuple of new hands; game replaces player's hand list |
| Dealer auto-play | `TurnManager.dealer_play()` | Hits until value ≥ 17 (no decision-making) |
| Resolve bets | `payouts.resolve_hand()` | Returns enum (WIN/LOSE/PUSH), not payout amounts |

## Integration Points

- `BlackjackGame.__init__()` expects `players: list[tuple[str, int]]` (name, starting bet pairs)
- Deck shuffles on creation; `draw()` pops from end of card list
- Insurance must be resolved before bet settlement (separate calls in game flow)
- Doubled bets are resolved in `PayoutResolver` using the `doubled` flag from `BetHand`

## Conventions

- **Enums** ([enums.py](../enums.py)): Use `TurnResult` for action outcomes, `GameResult` for hand settlement
- **Dataclasses**: `Card` and `Hand` are frozen (immutable); `BetHand`, `Player` are mutable
- **No external dependencies**: Pure Python stdlib only (dataclasses, enum, random)
