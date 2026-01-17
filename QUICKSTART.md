# Blackjack Web App - Quick Start Guide

## 🚀 Quick Start (2 Terminal Windows)

### Terminal 1 - Backend
```bash
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```
The API will run on http://localhost:8000

### Terminal 2 - Frontend  
```bash
cd frontend
npm install
npm run dev
```
The web app will run on http://localhost:5173

## 📖 How to Play

1. **Open** http://localhost:5173 in your browser
2. **Add players** - Enter player names and bets (1-4 players)
3. **Click "Start Game"** - Cards are dealt automatically
4. **Play your turn** - Use the action buttons:
   - **Hit**: Draw another card
   - **Stand**: End your turn
   - **Double**: Double your bet and draw one final card
   - **Split**: Split matching cards into two hands
5. **Insurance** - If dealer shows Ace, you can place insurance
6. **Game Over** - Results are displayed when all players finish
7. **New Game** - Click to start another round

## 🎮 Game Features

✅ Multiple players (1-4)
✅ Standard blackjack rules
✅ Hit, stand, double, split actions
✅ Insurance betting
✅ Dealer stands on soft 17
✅ Blackjack pays 3:2
✅ Clean, mobile-friendly UI
✅ Real-time game state updates

## 📡 API Endpoints

- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `POST /api/game/start` - Start new game
- `POST /api/game/{id}/hit` - Hit action
- `POST /api/game/{id}/stand` - Stand action
- `POST /api/game/{id}/double` - Double action
- `POST /api/game/{id}/split` - Split action
- `POST /api/game/{id}/insurance` - Place insurance
- `POST /api/game/{id}/resolve` - Resolve game

## 🧪 Testing

### Backend API Tests
```bash
pytest test_api.py -v
```

### Core Game Tests
```bash
pytest
```

### Coverage Report
```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.8+
- **Frontend**: React 18 + Vite
- **Testing**: pytest + requests
- **No Docker required** - Simple local development

## 📝 Notes

- Starting balance: $1000 (for tracking wins/losses)
- Balances are not persisted (reset each game session)
- All bets are imaginary (no real money)
- Game state is stored in memory (not persistent)

## 🐛 Troubleshooting

**Backend won't start?**
- Check Python version: `python --version` (needs 3.8+)
- Install dependencies: `pip install -r backend/requirements.txt`

**Frontend won't start?**
- Check Node version: `node --version` (needs 16+)
- Clear and reinstall: `rm -rf node_modules package-lock.json && npm install`

**Can't connect?**
- Backend must be running on port 8000
- Frontend must be running on port 5173
- Check for port conflicts: `lsof -i :8000` or `lsof -i :5173`

## 🎯 Development

The app uses hot reload - changes to files will automatically update:
- Backend: Auto-reloads when Python files change
- Frontend: Auto-updates in browser when React files change

Enjoy playing! 🎰
