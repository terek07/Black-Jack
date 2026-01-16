import { useState } from 'react';
import './GameSetup.css';

function GameSetup({ onStartGame }) {
  const [players, setPlayers] = useState([{ name: '', bet: 100 }]);

  const addPlayer = () => {
    if (players.length < 4) {
      setPlayers([...players, { name: '', bet: 100 }]);
    }
  };

  const removePlayer = (index) => {
    if (players.length > 1) {
      setPlayers(players.filter((_, i) => i !== index));
    }
  };

  const updatePlayer = (index, field, value) => {
    const updated = [...players];
    updated[index][field] = field === 'bet' ? parseInt(value) || 0 : value;
    setPlayers(updated);
  };

  const handleStart = () => {
    if (players.every(p => p.name.trim() && p.bet > 0)) {
      onStartGame(players);
    } else {
      alert('Please fill in all player names and ensure bets are greater than 0');
    }
  };

  return (
    <div className="game-setup">
      <h2>Setup Game</h2>
      <div className="players-list">
        {players.map((player, index) => (
          <div key={index} className="player-input">
            <input
              type="text"
              placeholder={`Player ${index + 1} Name`}
              value={player.name}
              onChange={(e) => updatePlayer(index, 'name', e.target.value)}
            />
            <input
              type="number"
              placeholder="Bet"
              value={player.bet}
              onChange={(e) => updatePlayer(index, 'bet', e.target.value)}
              min="1"
            />
            {players.length > 1 && (
              <button 
                className="danger" 
                onClick={() => removePlayer(index)}
              >
                Remove
              </button>
            )}
          </div>
        ))}
      </div>
      <div className="setup-actions">
        {players.length < 4 && (
          <button className="secondary" onClick={addPlayer}>
            Add Player
          </button>
        )}
        <button className="primary" onClick={handleStart}>
          Start Game
        </button>
      </div>
    </div>
  );
}

export default GameSetup;
