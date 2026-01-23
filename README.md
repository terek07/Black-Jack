# Blackjack Web App (FastAPI + React)

## Overview
Pełny stack: React (Vite) frontend + FastAPI backend + czysty Python engine.

- **Frontend:** React (Vite), dynamiczne UI, polling REST API
- **Backend:** FastAPI, REST API, CORS, pamięć RAM (brak bazy)
- **Engine:** Python, immutable dataclasses, logika blackjacka

## Szybki start (Quickstart)

### 1. Uruchom backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- Domyślnie backend nasłuchuje na porcie 8000
- Jeśli używasz Codespaces: ustaw port 8000 jako **Public** w zakładce "Ports"

### 2. Uruchom frontend

```bash
cd frontend
export VITE_API_BASE_URL=https://ubiquitous-space-waffle-pxj574g6xgph9jw-8000.app.github.dev  # (w Codespaces)
npm run dev
```
- Lokalnie: nie ustawiaj zmiennej, domyślnie łączy się z localhost:8000
- W Codespaces: podaj pełny adres backendu (patrz adres w "Ports")

### 3. Otwórz aplikację

- Lokalnie: http://localhost:5173
- Codespaces: link do portu 5173 (np. https://<twoj-codespace>-5173.app.github.dev)

## Najczęstsze problemy

- **CORS error:** Upewnij się, że port 8000 jest Public w Codespaces
- **Nie działa API:** Sprawdź czy oba serwery są uruchomione i adresy się zgadzają

## Testy

```bash
pytest
```
- 100% pokrycia testami (unit + integracyjne)

## Architektura

- **frontend/src/**: React, Vite, komponenty UI
- **backend/main.py**: FastAPI, REST API, CORS
- **engine/**: logika gry, modele, menedżery
- **tests/**: testy jednostkowe i integracyjne

## API (REST)

- `POST /api/game/start` – start nowej gry
- `POST /api/game/{game_id}/hit|stand|double|split|insurance` – akcje gracza (wymaga `player_index`, `hand_index`)
- `POST /api/game/{game_id}/resolve` – dociągnięcie krupiera + rozliczenie
- `GET /api/game/{game_id}` – aktualny stan gry (dealer pokazuje tylko jedną kartę do końca tury graczy)

### Struktura odpowiedzi gry
- `game_id`: identyfikator gry
- `players[]`: `name`, `balance`, `insurance_bet`, `hands[]` (`bet`, `doubled`, `is_finished`, `cards[]`, `value`, `is_blackjack`, `is_bust`)
- `dealer_hand`: lista kart (ukryta do czasu rozliczenia)
- `current_player_index`: indeks aktywnego gracza lub `null` gdy tury skończone
- `game_over`: true, gdy wszystkie ręce zakończone
- przy `/resolve`: `results[]` (payouty, blackjack/bust, saldo końcowe)

## Konfiguracja i porty

- Backend: port **8000** (`uvicorn main:app --reload --port 8000`)
- Frontend: port **5173** (`npm run dev`)
- Codespaces: ustaw port 8000 jako **Public** (inaczej proxy zablokuje CORS)
- Zmienna `VITE_API_BASE_URL` (frontend): pełny URL backendu (np. `https://<codespace>-8000.app.github.dev`); lokalnie nie ustawiaj – użyje `http://localhost:8000`
- CORS: backend obecnie zezwala na wszystkie originy (credentials = false); zmień w [backend/main.py](backend/main.py) w razie potrzeby

## Silnik gry (engine)

- [engine/models.py](engine/models.py): `Card`, `Hand` (liczenie asów 11→1), `BetHand`, `Player`
- [engine/game.py](engine/game.py): orkiestracja, kolejki tur, autostand przy blackjacku
- [engine/turns.py](engine/turns.py): `hit`, `stand`, `double` (double kończy turę)
- [engine/split.py](engine/split.py): walidacja i rozbijanie par (dobiera po jednej karcie)
- [engine/insurance.py](engine/insurance.py): ubezpieczenie do 1/2 stawki, wypłata 2:1
- [engine/payouts.py](engine/payouts.py): zasady wypłat (blackjack 3:2, dealer stoi na soft 17)

## Reguły blackjacka (skrót)

- Blackjack (2‑karty 21) bije inne 21, płaci 3:2
- Dealer stoi na soft 17
- Double tylko przy 2 kartach; kończy turę
- Split wymaga pary o tej samej wartości, każda ręka dostaje jedną nową kartę
- Insurance dostępne gdy dealer pokazuje Asa, max 1/2 zakładu, płaci 2:1 gdy dealer ma blackjacka

## Testy i pokrycie

- Uruchom wszystkie testy: `pytest`
- Raport z pokrycia: `pytest --cov=. --cov-report=html` (wynik w `htmlcov/`)

## Autor
- terek07
