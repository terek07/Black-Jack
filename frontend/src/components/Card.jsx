import './Card.css';

const suitSymbols = {
  'Hearts': '♥',
  'Diamonds': '♦',
  'Clubs': '♣',
  'Spades': '♠'
};

const valueLabels = {
  11: 'A',
  13: 'K',
  12: 'Q',
  // Jack has value of face card value which varies
};

function Card({ suit, value }) {
  const isRed = suit === 'Hearts' || suit === 'Diamonds';
  const suitSymbol = suitSymbols[suit] || suit;
  
  let displayValue = value;
  if (value === 11) displayValue = 'A';
  else if (value === 13) displayValue = 'K';
  else if (value === 12) displayValue = 'Q';
  else if (value === 10 && suit) displayValue = 'J';

  return (
    <div className={`card ${isRed ? 'red' : 'black'}`}>
      <div className="card-corner top-left">
        <div className="value">{displayValue}</div>
        <div className="suit">{suitSymbol}</div>
      </div>
      <div className="card-center">
        <div className="suit-large">{suitSymbol}</div>
      </div>
      <div className="card-corner bottom-right">
        <div className="value">{displayValue}</div>
        <div className="suit">{suitSymbol}</div>
      </div>
    </div>
  );
}

export default Card;
