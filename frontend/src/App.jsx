import { useState } from 'react';
import './App.css';
import GameSetup from './components/GameSetup';
import GameBoard from './components/GameBoard';

function App() {
  const [gameId, setGameId] = useState(null);
  const [gameState, setGameState] = useState(null);

  const startNewGame = async (players) => {
    try {
      const response = await fetch('http://localhost:8000/api/game/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ players })
      });
      const data = await response.json();
      setGameId(data.game_id);
      setGameState(data);
    } catch (error) {
      console.error('Error starting game:', error);
    }
  };

  const resetGame = () => {
    setGameId(null);
    setGameState(null);
  };

  return (
    <div className="App">
      <h1>♠️ Blackjack ♥️</h1>
      {!gameId ? (
        <GameSetup onStartGame={startNewGame} />
      ) : (
        <GameBoard 
          gameId={gameId} 
          initialGameState={gameState}
          onReset={resetGame}
        />
      )}
    </div>
  );
}

export default App;
