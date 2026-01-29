# Blackjack Web App (FastAPI + React)

A full-stack Blackjack web application built for learning and demonstration purposes.

- Frontend: React (Vite) — interactive UI, communicates with backend via REST.
- Backend: FastAPI — exposes a small REST API and holds in-memory game state.
- Game engine: Pure Python — immutable dataclasses and clear manager classes implement Blackjack rules.

This repository implements the classic Blackjack ruleset (dealer stands on soft 17, natural blackjack pays 3:2, split/double/insurance are supported) and is designed to be easy to run locally, test, and extend.

---

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Download \& Setup](#download--setup)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Engine Design \& Key Concepts](#engine-design--key-concepts)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

---


## Features

- Multiplayer support (1–4 players) in a single game session
- Player actions: hit, stand, double, split, and place insurance
- Dealer behavior: stands on soft 17
- Natural blackjack pays 3:2
- In-memory game state (no database) — lightweight and easy to run
- Full unit and integration test coverage

## Technologies

- Frontend: React, Vite, JavaScript
- Backend: Python, FastAPI, Uvicorn
- Game engine: Python 3 dataclasses, enums, and standard library only
- Testing: pytest

---

## Download & Setup

Prerequisites:

- Python 3.10+ (3.12 recommended)
- Node.js 16+ and npm

Clone the repository:

```powershell
git clone https://github.com/<your-username>/Black-Jack.git
cd Black-Jack
```

Install backend dependencies:

```powershell
cd backend; python -m pip install -r requirements.txt
```

Install frontend dependencies:

```powershell
cd ..\frontend; npm install
```

Notes:
- The backend runs on port 8000 by default. The frontend dev server runs on port 5173.
- CORS is configured for local development. If you change ports, update the CORS origins in `backend/main.py` or set `VITE_API_BASE_URL` for the frontend.

---

## Quick Start

Run the backend (from the `backend` directory):

```powershell
cd backend
uvicorn main:app --reload --port 8000
```

Run the frontend (from the `frontend` directory):

```powershell
cd frontend
npm run dev
```

Open the UI in your browser at:

- http://localhost:5173 (frontend)
- API docs (FastAPI): http://localhost:8000/docs

---

## Project Structure

Top-level layout:

- `frontend/` — React + Vite application (UI components, assets)
- `backend/` — FastAPI app exposing REST endpoints
- `engine/` — Python package with game logic, models and managers
- `tests/` — Unit and integration tests (pytest)

Important source files (high-level):

- `frontend/src/App.jsx` — root React component and session state
- `frontend/src/components/GameBoard.jsx` — main game UI and polling logic
- `backend/main.py` — FastAPI application, in-memory `games` store, JSON serialization helpers
- `engine/models.py` — dataclasses: `Card`, `Hand`, `BetHand`, `Player`
- `engine/game.py` — `BlackjackGame` orchestrator and facade methods
- `engine/turns.py`, `engine/split.py`, `engine/insurance.py`, `engine/payouts.py` — specialized manager classes

---

## Engine Design & Key Concepts

Design goals:

- Separation of concerns: UI, API, and domain logic are separate and easy to reason about.
- Immutability: core value objects (`Card`, `Hand`) are frozen dataclasses to avoid accidental mutation.
- Single responsibility: managers encapsulate actions (turns, splits, insurance, payouts).

Key behaviors and rules implemented:

- Ace logic: Aces count as 11 until the total would exceed 21, then are downgraded to 1 (handled in `Hand.value`).
- Blackjack detection: Only a 2-card 21 is considered a natural blackjack (beats other 21s).
- Double: Allowed only on the initial 2-card hand; it doubles the bet, draws exactly one card, and finishes the hand.
- Split: Allowed when the two starting cards have equal value; creates two hands with equal bets and one extra card drawn for each.
- Insurance: Available when dealer shows an Ace; max insurance is half the hand bet and pays 2:1 on dealer blackjack.
- Dealer play: Dealer hits until hand value is 17 or higher and stands on soft 17.

Deck:

- `engine/deck.py` provides a shuffled 52-card deck. `draw()` pops from the end — the deck is finite and can be exhausted in long tests or custom scenarios.

Error handling and validation:

- Managers raise `ValueError` for invalid actions (e.g., illegal split/double/insurance).
- `can_<action>()` methods exist to check preconditions before performing actions.

---

## API Endpoints

Base path: `/api/game`

- `POST /api/game/start` — create a new game; payload: list of player name + starting bet
- `GET /api/game/{game_id}` — get current game state (dealer first card hidden until players finish)
- `POST /api/game/{game_id}/hit|stand|double|split|insurance` — player actions (require `player_index` and `hand_index` in body)
- `POST /api/game/{game_id}/resolve` — resolves dealer play and settles bets

Response shape highlights:

- `players[]`: each player has `name`, `balance`, `insurance_bet`, and `hands[]` with `bet`, `doubled`, `is_finished`, `cards[]`, `value`, `is_blackjack`, `is_bust`.
- `dealer_hand`: list of cards (first card may be hidden depending on `show_dealer_cards` flag)
- `current_player_index`: index of the player whose turn is active (or `null` if players are done)
- `game_over`: boolean flag indicating the game finished and results are final

---

## Testing

Run the full test suite with pytest from the project root:

```powershell
pytest -q
```

- The test suite includes unit tests for engine components and integration tests that exercise end-to-end flows.
- Tests create Card instances directly for deterministic scenarios (preferred to avoid deck state coupling).