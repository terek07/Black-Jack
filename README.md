# Blackjack Web Application

A full-stack Blackjack game with FastAPI backend and React frontend.

## Features

- ✨ Multiplayer support (up to 4 players)
- 💰 Imaginary betting system
- 🎴 Classic blackjack rules (hit, stand, double, split)
- 🛡️ Insurance betting when dealer shows Ace
- 🎨 Modern, mobile-friendly UI
- 🃏 Simple card design with suit symbols

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Frontend:**
- React 18
- Vite (build tool)
- CSS3 (styling)

## Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── App.jsx       # Main app component
│   │   └── index.css     # Global styles
│   └── package.json      # Node dependencies
├── game.py               # Core game logic
├── models.py             # Data models
├── deck.py               # Deck management
├── turns.py              # Turn manager
├── split.py              # Split manager
├── insurance.py          # Insurance manager
└── payouts.py            # Payout resolver
```

## Installation

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Start the backend server:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## How to Play

1. **Setup**: Enter player names and initial bets (1-4 players)
2. **Insurance**: If dealer shows an Ace, you can place insurance (up to half your bet)
3. **Actions**:
   - **Hit**: Draw another card
   - **Stand**: End your turn
   - **Double**: Double your bet and draw one final card (only with 2 cards)
   - **Split**: Split matching cards into two hands (only with 2 cards of same value)
4. **Winning**: Beat the dealer without going over 21!

## Game Rules

- Dealer stands on soft 17
- Blackjack (natural 21) pays 3:2 and beats regular 21
- Insurance pays 2:1 when dealer has blackjack
- Doubled hands pay double winnings
- Aces count as 11 or 1 (automatically adjusted)

## API Endpoints

- `POST /api/game/start` - Start new game
- `POST /api/game/{game_id}/hit` - Hit action
- `POST /api/game/{game_id}/stand` - Stand action
- `POST /api/game/{game_id}/double` - Double action
- `POST /api/game/{game_id}/split` - Split action
- `POST /api/game/{game_id}/insurance` - Place insurance
- `POST /api/game/{game_id}/resolve` - Resolve game
- `GET /api/game/{game_id}` - Get game state

## Testing

Run the existing test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## Development

- Backend runs on port 8000
- Frontend runs on port 5173
- CORS is configured to allow local development
- Hot reload enabled for both backend and frontend

## Future Enhancements

- [ ] Persistent player balances
- [ ] Game history
- [ ] Sound effects
- [ ] Animations
- [ ] Multiple deck support
- [ ] Betting limits configuration
- [ ] Tournament mode

## License

MIT
