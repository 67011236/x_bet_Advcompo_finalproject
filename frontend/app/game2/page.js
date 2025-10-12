"use client";
import { useState, useEffect } from "react";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "../../styles/game2.css";

const CHOICES = {
  rock: { name: "Rock", emoji: "✊", beats: "scissors" },
  paper: { name: "Paper", emoji: "✋", beats: "rock" },
  scissors: { name: "Scissors", emoji: "✌️", beats: "paper" }
};

export default function Game2() {
  const [balance, setBalance] = useState(0);
  const [betAmount, setBetAmount] = useState(0);
  const [playerChoice, setPlayerChoice] = useState(null);
  const [botChoice, setBotChoice] = useState(null);
  const [gameResult, setGameResult] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [gameHistory, setGameHistory] = useState([]);
  const [showResult, setShowResult] = useState(false);
  const [showRandomizePopup, setShowRandomizePopup] = useState(false);
  const [randomizeText, setRandomizeText] = useState("");
  const [showFinalResult, setShowFinalResult] = useState(false);
  const [finalResultData, setFinalResultData] = useState(null);

  // Fetch user balance
  useEffect(() => {
    fetchBalance();
  }, []);

  const fetchBalance = async () => {
    try {
      const response = await fetch("http://localhost:8000/balance", {
        credentials: "include",
      });
      if (response.ok) {
        const data = await response.json();
        setBalance(data.amount);
      }
    } catch (error) {
      console.error("Error fetching balance:", error);
    }
  };

  const adjustBetAmount = (change) => {
    const newAmount = betAmount + change;
    if (newAmount >= 0) {
      setBetAmount(newAmount);
    }
  };

  const setBetToAllIn = () => {
    setBetAmount(balance);
  };

  const getRandomChoice = () => {
    const choices = Object.keys(CHOICES);
    return choices[Math.floor(Math.random() * choices.length)];
  };

  const determineWinner = (playerChoice, botChoice) => {
    if (playerChoice === botChoice) return "tie";
    if (CHOICES[playerChoice].beats === botChoice) return "win";
    return "lose";
  };

  const playGame = async () => {
    if (!playerChoice || betAmount > balance || betAmount <= 0) return;
    
    setIsPlaying(true);
    setShowResult(false);
    setBotChoice(null); // Clear previous bot choice
    setShowRandomizePopup(true); // Show popup
    
    // Randomize text animations
    const texts = [
      "🎲 Bot is thinking...",
      "🎯 Analyzing patterns...",
      "🔥 Making decision...",
      "⚡ Almost ready...",
      "🎪 Final choice..."
    ];
    
    let textIndex = 0;
    const textInterval = setInterval(() => {
      setRandomizeText(texts[textIndex % texts.length]);
      textIndex++;
    }, 400);
    
    // Start randomization animation
    const animationDuration = 2500; // 2.5 seconds
    const intervalDuration = 120; // Change choice every 120ms
    let currentIndex = 0;
    const choices = Object.keys(CHOICES);
    
    const randomizeInterval = setInterval(() => {
      setBotChoice(choices[currentIndex % choices.length]);
      currentIndex++;
    }, intervalDuration);
    
    // Stop randomization and set final choice
    setTimeout(() => {
      clearInterval(randomizeInterval);
      clearInterval(textInterval);
      
      setRandomizeText("🎉 Choice made!");
      
      // Generate final bot choice
      const botMove = getRandomChoice();
      setBotChoice(botMove);
      
      // Show final choice for a moment, then show results
      setTimeout(() => {
        // Determine result
        const result = determineWinner(playerChoice, botMove);
        setGameResult(result);
        
        // Calculate winnings
        let winAmount = 0;
        let newBalance = balance;
        
        if (result === "win") {
          winAmount = betAmount * 2;
          newBalance = balance + winAmount - betAmount;
        } else if (result === "tie") {
          winAmount = betAmount;
          newBalance = balance; // No change for tie
        } else {
          newBalance = balance - betAmount;
        }

        // Prepare result data for popup
        const resultData = {
          playerChoice,
          botChoice: botMove,
          result,
          betAmount,
          winAmount: result === "lose" ? 0 : winAmount,
          balanceChange: result === "win" ? winAmount - betAmount : 
                        result === "lose" ? -betAmount : 0,
          newBalance
        };
        
        setFinalResultData(resultData);
        setShowFinalResult(true);
        
        // Update balance via Game2 API
        (async () => {
          try {
            const response = await fetch("http://localhost:8000/api/game2/play", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              credentials: "include",
              body: JSON.stringify({
                bet_amount: betAmount,
                player_choice: playerChoice,
                bot_choice: botMove,
                result: result
              })
            });
            
            if (response.ok) {
              const data = await response.json();
              if (data.success) {
                // Update balance from API response
                setBalance(data.result.balance_after);
                console.log("Game2 result saved to database:", data.result);
              }
            } else {
              console.error("Failed to save game result");
            }
          } catch (error) {
            console.error("Error saving game result:", error);
          }
        })();
        
        // Add to game history
        const gameRecord = {
          id: Date.now(),
          playerChoice,
          botChoice: botMove,
          result,
          betAmount,
          winAmount: result === "lose" ? 0 : winAmount,
          timestamp: new Date().toLocaleTimeString()
        };
        
        setGameHistory(prev => [gameRecord, ...prev.slice(0, 4)]);
        
        // Don't auto-hide popup - let user click play again
        setIsPlaying(false);
        
      }, 800);
      
    }, animationDuration);
  };

  const resetGame = () => {
    setPlayerChoice(null);
    setBotChoice(null);
    setGameResult(null);
    setShowResult(false);
    setShowRandomizePopup(false);
    setShowFinalResult(false);
    setFinalResultData(null);
  };

  const getResultMessage = () => {
    if (!gameResult) return "";
    switch (gameResult) {
      case "win": return `You Win! +${betAmount} THB`;
      case "lose": return `You Lose! -${betAmount} THB`;
      case "tie": return "It's a Tie!";
      default: return "";
    }
  };

  const getResultClass = () => {
    switch (gameResult) {
      case "win": return "result-win";
      case "lose": return "result-lose";
      case "tie": return "result-tie";
      default: return "";
    }
  };

  return (
    <Protected>
      <div className="game2-page">
        <AuthenticatedHeader />
        
        <div className="game-container">
          <div className="game-layout">
            {/* Left Column: Bot Section + Recent Games */}
            <div className="left-column">
              {/* Bot Section */}
              <div className={`bot-section ${isPlaying ? "randomizing" : ""}`}>
                <h2>BOT</h2>
                <div className={`bot-choice ${isPlaying ? "randomizing" : ""}`}>
                  {botChoice && !isPlaying ? (
                    <div className="choice-display">
                      <span className="choice-emoji">{CHOICES[botChoice].emoji}</span>
                      <span className="choice-name">{CHOICES[botChoice].name}</span>
                    </div>
                  ) : isPlaying && botChoice ? (
                    <div className="choice-display">
                      <span className={`choice-emoji ${isPlaying ? "randomizing" : ""}`}>
                        {CHOICES[botChoice].emoji}
                      </span>
                      <span className={`choice-name ${isPlaying ? "randomizing" : ""}`}>
                        {CHOICES[botChoice].name}
                      </span>
                    </div>
                  ) : (
                    <div className="choice-placeholder">
                      <span className="choice-emoji">
                        {isPlaying ? "🎲" : "❓"}
                      </span>
                      <span className="choice-name">
                        {isPlaying ? "Randomizing..." : "Waiting"}
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Game History */}
              {gameHistory.length > 0 && (
                <div className="game-history">
                  <h3>Recent Games</h3>
                  <div className="history-list">
                    {gameHistory.map((game) => (
                      <div key={game.id} className={`history-item ${game.result}`}>
                        <div className="history-choices">
                          <span>{CHOICES[game.playerChoice].emoji}</span>
                          <span className="vs">vs</span>
                          <span>{CHOICES[game.botChoice].emoji}</span>
                        </div>
                        <div className="history-result">
                          {game.result === "win" ? `+${game.winAmount - game.betAmount}` : 
                           game.result === "lose" ? `-${game.betAmount}` : "±0"} THB
                        </div>
                        <div className="history-time">{game.timestamp}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Game Controls */}
            <div className="game-controls">
              {/* Player Selection */}
              <div className="player-section">
                <h3>Select your choice</h3>
                <div className="choices-grid">
                  {Object.entries(CHOICES).map(([key, choice]) => (
                    <button
                      key={key}
                      className={`choice-button ${playerChoice === key ? "selected" : ""} ${isPlaying ? "disabled" : ""}`}
                      onClick={() => !isPlaying && setPlayerChoice(key)}
                      disabled={isPlaying}
                    >
                      <span className="choice-emoji">{choice.emoji}</span>
                      <span className="choice-name">{choice.name}</span>
                    </button>
                  ))}
                </div>
                
                {/* Game Rules */}
                <div className="game-rules">
                  <h4>Game Rules</h4>
                  <div className="rules-list">
                    <div className="rule-item">
                      <span className="rule-emoji">✊</span>
                      <span className="rule-text">Rock beats Scissors</span>
                    </div>
                    <div className="rule-item">
                      <span className="rule-emoji">✋</span>
                      <span className="rule-text">Paper beats Rock</span>
                    </div>
                    <div className="rule-item">
                      <span className="rule-emoji">✌️</span>
                      <span className="rule-text">Scissors beats Paper</span>
                    </div>
                    <div className="rule-item payout">
                      <span className="rule-emoji">🎯</span>
                      <span className="rule-text">Win = 2x your bet | Tie = bet returned</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Result Display */}
              {showResult && (
                <div className={`game-result ${getResultClass()}`}>
                  <div className="result-message">{getResultMessage()}</div>
                  <button className="play-again-btn" onClick={resetGame}>
                    Play Again
                  </button>
                </div>
              )}
            </div>

            {/* Betting Section */}
            <div className="betting-section">
              {/* Your Balance - Orange Box */}
              <div style={{
                background: "linear-gradient(135deg, #ff9233 0%, #ff7a00 100%)",
                borderRadius: "15px",
                padding: "15px",
                textAlign: "center",
                color: "white",
                marginBottom: "20px",
                boxShadow: "0 6px 20px rgba(255, 146, 51, 0.25)"
              }}>
                <div style={{ fontSize: "14px", fontWeight: "600", marginBottom: "6px" }}>Your Balance</div>
                <div style={{ fontSize: "24px", fontWeight: "bold", letterSpacing: "0.5px" }}>💰 {Math.floor(balance)} coins</div>
              </div>

              {/* Bet Amount */}
              <div style={{ marginBottom: "20px" }}>
                <h3 style={{ 
                  color: "white", 
                  fontSize: "16px", 
                  fontWeight: "bold", 
                  marginBottom: "15px",
                  textAlign: "center"
                }}>Bet Amount</h3>
                
                {/* Main bet control row */}
                <div style={{ display: "flex", gap: "8px", alignItems: "center", width: "100%", marginBottom: "12px" }}>
                  <button
                    onClick={() => adjustBetAmount(-10)}
                    disabled={isPlaying || betAmount < 10}
                    style={{
                      background: "#dc3545",
                      color: "white",
                      border: "none",
                      borderRadius: "10px",
                      padding: "10px 15px",
                      cursor: isPlaying || betAmount < 10 ? "not-allowed" : "pointer",
                      fontWeight: "bold",
                      fontSize: "14px",
                      minWidth: "55px",
                      boxShadow: "0 3px 8px rgba(220, 53, 69, 0.25)",
                      transition: "all 0.3s ease",
                      opacity: isPlaying || betAmount < 10 ? 0.5 : 1
                    }}
                  >
                    -10
                  </button>
                  
                  <input
                    type="number"
                    value={betAmount}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0;
                      if (value >= 0 && value <= balance) {
                        setBetAmount(value);
                      }
                    }}
                    disabled={isPlaying}
                    min="0"
                    max={balance}
                    style={{
                      flex: 1,
                      padding: "10px 15px",
                      background: "rgba(255, 255, 255, 0.1)",
                      borderRadius: "10px",
                      textAlign: "center",
                      fontSize: "18px",
                      fontWeight: "bold",
                      color: "white",
                      border: "2px solid rgba(255, 255, 255, 0.2)",
                      minHeight: "40px",
                      outline: "none",
                      cursor: isPlaying ? "not-allowed" : "text",
                      opacity: isPlaying ? 0.5 : 1,
                      transition: "all 0.3s ease"
                    }}
                    onFocus={(e) => {
                      e.target.style.border = "2px solid #007bff";
                      e.target.style.background = "rgba(255, 255, 255, 0.15)";
                    }}
                    onBlur={(e) => {
                      e.target.style.border = "2px solid rgba(255, 255, 255, 0.2)";
                      e.target.style.background = "rgba(255, 255, 255, 0.1)";
                    }}
                  />
                  
                  <button
                    onClick={() => adjustBetAmount(10)}
                    disabled={isPlaying}
                    style={{
                      background: "#28a745",
                      color: "white",
                      border: "none",
                      borderRadius: "10px",
                      padding: "10px 15px",
                      cursor: isPlaying ? "not-allowed" : "pointer",
                      fontWeight: "bold",
                      fontSize: "14px",
                      minWidth: "55px",
                      boxShadow: "0 3px 8px rgba(40, 167, 69, 0.25)",
                      transition: "all 0.3s ease",
                      opacity: isPlaying ? 0.5 : 1
                    }}
                  >
                    +10
                  </button>
                </div>
                
                {/* Preset buttons */}
                <div style={{ 
                  display: "grid", 
                  gridTemplateColumns: "1fr 1fr 1fr",
                  gap: "8px", 
                  marginBottom: "15px"
                }}>
                  {[25, 50, 100].map(amount => (
                    <button
                      key={amount}
                      onClick={() => setBetAmount(amount)}
                      disabled={isPlaying}
                      style={{
                        background: betAmount === amount ? "#007bff" : "rgba(255, 255, 255, 0.15)",
                        color: "white",
                        border: betAmount === amount ? "2px solid #0056b3" : "2px solid rgba(255, 255, 255, 0.2)",
                        borderRadius: "8px",
                        padding: "8px 12px",
                        cursor: isPlaying ? "not-allowed" : "pointer",
                        fontSize: "14px",
                        fontWeight: "bold",
                        transition: "all 0.3s ease",
                        boxShadow: betAmount === amount ? "0 3px 8px rgba(0, 123, 255, 0.25)" : "0 2px 6px rgba(0, 0, 0, 0.1)",
                        opacity: isPlaying ? 0.5 : 1
                      }}
                    >
                      {amount}
                    </button>
                  ))}
                </div>
              </div>

              {/* ALL IN Button */}
              <button
                onClick={setBetToAllIn}
                disabled={isPlaying || balance <= 0}
                style={{
                  background: isPlaying || balance <= 0 ? "#6b7280" : "linear-gradient(135deg, #17a2b8 0%, #138496 100%)",
                  color: "white",
                  border: "none",
                  borderRadius: "12px",
                  padding: "12px 20px",
                  cursor: isPlaying || balance <= 0 ? "not-allowed" : "pointer",
                  fontWeight: "bold",
                  fontSize: "14px",
                  width: "100%",
                  opacity: isPlaying || balance <= 0 ? 0.5 : 1,
                  transition: "all 0.3s ease",
                  boxShadow: balance > 0 && !isPlaying ? "0 4px 15px rgba(23, 162, 184, 0.25)" : "none",
                  letterSpacing: "0.5px",
                  marginBottom: "15px"
                }}
              >
                🚀 ALL IN ({Math.floor(balance)} coins)
              </button>
              
              {/* Place Bet Button */}
              <button
                className={`place-bet-btn ${!playerChoice || isPlaying || betAmount <= 0 ? "disabled" : ""}`}
                onClick={playGame}
                disabled={!playerChoice || isPlaying || betAmount <= 0}
              >
                {isPlaying ? "Playing..." : "Place Bet"}
              </button>
            </div>
          </div>


        </div>

        {/* Randomization Popup */}
        {showRandomizePopup && (
          <div className="randomization-overlay">
            <div className="randomization-content">
              {!showFinalResult ? (
                <>
                  <div className="randomization-title">Rock Paper Scissors</div>
                  <div className="randomization-emoji">
                    {botChoice ? CHOICES[botChoice].emoji : "🎲"}
                  </div>
                  <div className="randomization-text">{randomizeText}</div>
                  <div style={{
                    display: "flex",
                    justifyContent: "center",
                    gap: "15px",
                    marginTop: "20px",
                    opacity: 0.7
                  }}>
                    <span style={{ fontSize: "2rem", animation: "pulse 0.6s infinite alternate" }}>✊</span>
                    <span style={{ fontSize: "2rem", animation: "pulse 0.6s infinite alternate 0.2s" }}>✋</span>
                    <span style={{ fontSize: "2rem", animation: "pulse 0.6s infinite alternate 0.4s" }}>✌️</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="result-popup-header">
                    <div className={`result-title ${finalResultData?.result}`}>
                      {finalResultData?.result === "win" ? "🎉 YOU WIN!" : 
                       finalResultData?.result === "lose" ? "😔 YOU LOSE!" : 
                       "🤝 IT'S A TIE!"}
                    </div>
                  </div>
                  
                  <div className="choices-comparison">
                    <div className="bot-result">
                      <div className="choice-label">Bot</div>
                      <div className="choice-big-emoji">
                        {finalResultData ? CHOICES[finalResultData.botChoice].emoji : ""}
                      </div>
                      <div className="choice-name-big">
                        {finalResultData ? CHOICES[finalResultData.botChoice].name : ""}
                      </div>
                    </div>
                    
                    <div className="vs-divider">VS</div>
                    
                    <div className="player-result">
                      <div className="choice-label">You</div>
                      <div className="choice-big-emoji">
                        {finalResultData ? CHOICES[finalResultData.playerChoice].emoji : ""}
                      </div>
                      <div className="choice-name-big">
                        {finalResultData ? CHOICES[finalResultData.playerChoice].name : ""}
                      </div>
                    </div>
                  </div>
                  
                  <div className="result-summary">
                    <div className="bet-info">
                      <span>Bet Amount: </span>
                      <span className="amount">{finalResultData?.betAmount} THB</span>
                    </div>
                    <div className={`balance-change ${finalResultData?.result}`}>
                      {finalResultData?.result === "win" ? (
                        <>
                          <span>You Won: </span>
                          <span className="amount">+{finalResultData?.balanceChange} THB</span>
                        </>
                      ) : finalResultData?.result === "lose" ? (
                        <>
                          <span>You Lost: </span>
                          <span className="amount">{finalResultData?.balanceChange} THB</span>
                        </>
                      ) : (
                        <>
                          <span>No Change: </span>
                          <span className="amount">0 THB</span>
                        </>
                      )}
                    </div>
                    <div className="new-balance">
                      <span>New Balance: </span>
                      <span className="amount">{finalResultData?.newBalance?.toFixed(2)} THB</span>
                    </div>
                  </div>
                  
                  <div className="result-explanation">
                    {finalResultData?.result === "win" && (
                      <div className="explanation-text">
                        {CHOICES[finalResultData.playerChoice].name} beats {CHOICES[finalResultData.botChoice].name}!
                      </div>
                    )}
                    {finalResultData?.result === "lose" && (
                      <div className="explanation-text">
                        {CHOICES[finalResultData.botChoice].name} beats {CHOICES[finalResultData.playerChoice].name}!
                      </div>
                    )}
                    {finalResultData?.result === "tie" && (
                      <div className="explanation-text">
                        Both chose {CHOICES[finalResultData.playerChoice].name}!
                      </div>
                    )}
                  </div>
                  
                  <button 
                    className="popup-play-again-btn"
                    onClick={resetGame}
                  >
                    🎮 Play Again
                  </button>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </Protected>
  );
}