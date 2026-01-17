import { useState, useEffect } from 'react';
import './GameBoard.css';
import Card from './Card';

function GameBoard({ gameId, initialGameState, onReset }) {
  const [gameState, setGameState] = useState(initialGameState);
  const [loading, setLoading] = useState(false);
  const [insuranceAmount, setInsuranceAmount] = useState('');
  const [showInsurance, setShowInsurance] = useState(false);

  const formatCurrency = (amount) => {
    if (amount === 0) return '$0';
    const prefix = amount > 0 ? '+' : '-';
    return `${prefix}$${Math.abs(amount)}`;
  };

  const formatResultLabel = (result) => result.replace(/_/g, ' ');

  useEffect(() => {
    if (initialGameState) {
      const dealerUpCard = initialGameState.dealer_hand[0];
      if (dealerUpCard && dealerUpCard.value === 11) {
        setShowInsurance(true);
      }
    }
  }, [initialGameState]);

  useEffect(() => {
    if (gameState?.game_over && !gameState.results) {
      resolveGame();
    }
  }, [gameState]);

  const makeAction = async (action, playerIndex, handIndex = 0, extraData = {}) => {
    setLoading(true);
    try {
      const body = { game_id: gameId, player_index: playerIndex, hand_index: handIndex, ...extraData };
      const response = await fetch(`http://localhost:8000/api/game/${gameId}/${action}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await response.json();
      setGameState(data);
    } catch (error) {
      console.error(`Error during ${action}:`, error);
    } finally {
      setLoading(false);
    }
  };

  const resolveGame = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/api/game/${gameId}/resolve`, {
        method: 'POST'
      });
      const data = await response.json();
      setGameState(data);
    } catch (error) {
      console.error('Error resolving game:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInsurance = async (playerIndex) => {
    const amount = parseInt(insuranceAmount);
    const player = gameState.players[playerIndex];
    const maxInsurance = Math.floor(player.hands[0].bet / 2);
    
    if (amount > 0 && amount <= maxInsurance) {
      await makeAction('insurance', playerIndex, 0, { amount });
      setShowInsurance(false);
      setInsuranceAmount('');
    } else {
      alert(`Insurance must be between 1 and ${maxInsurance}`);
    }
  };

  const canSplit = (hand) => {
    return hand.cards.length === 2 && hand.cards[0].value === hand.cards[1].value && !hand.is_finished;
  };

  const canDouble = (hand) => {
    return hand.cards.length === 2 && !hand.doubled && !hand.is_finished;
  };

  if (!gameState) return <div>Loading...</div>;

  return (
    <div className="game-board">
      <div className="dealer-section">
        <h2>Dealer</h2>
        <div className="hand">
          <div className="cards">
            {gameState.dealer_hand.map((card, idx) => (
              <Card key={idx} suit={card.suit} value={card.value} />
            ))}
          </div>
          <div className="hand-value">Value: {gameState.dealer_value}</div>
        </div>
      </div>

      <div className="players-section">
        {gameState.players.map((player, playerIdx) => (
          <div 
            key={playerIdx} 
            className={`player-card ${playerIdx === gameState.current_player_index ? 'active' : ''}`}
          >
            <h3>{player.name}</h3>
            <div className="player-info">
              <span className="balance">Balance: ${player.balance}</span>
              {player.insurance_bet > 0 && (
                <span className="insurance">Insurance: ${player.insurance_bet}</span>
              )}
            </div>

            {showInsurance && playerIdx === gameState.current_player_index && (
              <div className="insurance-prompt">
                <input
                  type="number"
                  placeholder="Insurance amount ($)"
                  value={insuranceAmount}
                  onChange={(e) => setInsuranceAmount(e.target.value)}
                  max={Math.floor(player.hands[0].bet / 2)}
                />
                <button 
                  className="warning" 
                  onClick={() => handleInsurance(playerIdx)}
                  disabled={loading}
                >
                  Place Insurance
                </button>
                <button 
                  className="secondary" 
                  onClick={() => setShowInsurance(false)}
                  disabled={loading}
                >
                  Skip
                </button>
              </div>
            )}

            <div className="player-hands">
              {player.hands.map((hand, handIdx) => (
                <div key={handIdx} className="hand">
                  <div className="cards">
                    {hand.cards.map((card, cardIdx) => (
                      <Card key={cardIdx} suit={card.suit} value={card.value} />
                    ))}
                  </div>
                  <div className="hand-info">
                    <div className="hand-value">
                      Value: {hand.value}
                      {hand.is_blackjack && ' (Blackjack!)'}
                      {hand.is_bust && ' (Bust!)'}
                      {hand.doubled && ' (Doubled)'}
                    </div>
                    <div className="bet-amount">Bet: ${hand.bet}</div>
                  </div>

                  {!hand.is_finished && 
                   !hand.is_bust && 
                   playerIdx === gameState.current_player_index && 
                   !showInsurance && (
                    <div className="action-buttons">
                      <button
                        className="primary"
                        onClick={() => makeAction('hit', playerIdx, handIdx)}
                        disabled={loading}
                      >
                        Hit
                      </button>
                      <button
                        className="secondary"
                        onClick={() => makeAction('stand', playerIdx, handIdx)}
                        disabled={loading}
                      >
                        Stand
                      </button>
                      {canDouble(hand) && (
                        <button
                          className="warning"
                          onClick={() => makeAction('double', playerIdx, handIdx)}
                          disabled={loading}
                        >
                          Double
                        </button>
                      )}
                      {canSplit(hand) && (
                        <button
                          className="warning"
                          onClick={() => makeAction('split', playerIdx, handIdx)}
                          disabled={loading}
                        >
                          Split
                        </button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {gameState.game_over && (
        <div className="game-over">
          <h2>Game Over!</h2>
          {gameState.results && gameState.results.map((result, idx) => (
            <div key={idx} className="result-card">
              <div className="result-header">
                <strong>{result.player_name}</strong>
                <span className={`payout ${result.total_payout > 0 ? 'win' : result.total_payout < 0 ? 'loss' : 'push'}`}>
                  {result.total_payout > 0 ? 'WON' : result.total_payout < 0 ? 'LOST' : 'PUSH'} {formatCurrency(result.total_payout)}
                </span>
              </div>
              <div className="result-meta">
                <span>Final Balance: ${result.final_balance}</span>
                {result.insurance_payout !== 0 && (
                  <span>Insurance: {formatCurrency(result.insurance_payout)}</span>
                )}
              </div>
              <div className="hand-results">
                {result.hand_results.map((handResult) => (
                  <div key={handResult.hand_index} className="hand-result">
                    <div className="hand-label">Hand {handResult.hand_index + 1}</div>
                    <div className="hand-summary">
                      <span className="badge">{formatResultLabel(handResult.result)}</span>
                      <span>Bet: ${handResult.bet}</span>
                      <span>Payout: {formatCurrency(handResult.payout)}</span>
                      <span>Value: {handResult.hand_value}</span>
                      {handResult.is_blackjack && <span className="badge highlight">Blackjack</span>}
                      {handResult.is_bust && <span className="badge danger">Bust</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
          <button className="primary" onClick={onReset}>
            New Game
          </button>
        </div>
      )}
    </div>
  );
}

export default GameBoard;
