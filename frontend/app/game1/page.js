"use client";
import { useState, useEffect, useRef } from "react";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "./style.css";

export default function Game1() {
  const [balance, setBalance] = useState(1000);
  const [betAmount, setBetAmount] = useState(50);
  const [lastResult, setLastResult] = useState(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedColor, setSelectedColor] = useState("blue");
  const [isMounted, setIsMounted] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const wheelRef = useRef(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const spinWheel = () => {
    if (isSpinning || betAmount > balance || betAmount <= 0 || !isMounted) return;
    
    setIsSpinning(true);
    setLastResult(null);
    setShowResultModal(false); // Hide modal when starting new spin
    
    const wheel = wheelRef.current;
    if (!wheel) return;
    
    // Get current rotation (always accumulating in positive direction)
    const currentTransform = wheel.style.transform;
    const currentRotation = currentTransform ? 
      parseInt(currentTransform.match(/rotate\((-?\d+)deg\)/)?.[1] || 0) : 0;
    
    // Fixed rotation: always same amount of degrees in same direction (left to right = positive rotation)
    const fixedRotationDegrees = 1800; // Always rotate exactly 1800 degrees (5 full rotations)
    const randomFinalPosition = Math.floor(Math.random() * 360); // Random final position within one rotation
    const totalRotation = currentRotation + fixedRotationDegrees + randomFinalPosition;
    
    // Fixed 5 seconds duration
    const spinDuration = 5000;
    
    // Clear any existing transition
    wheel.style.transition = 'none';
    wheel.offsetHeight; // Force reflow
    
    // Apply smooth deceleration: starts fast, gradually slows down to stop
    // Using ease-out timing function for natural deceleration
    wheel.style.transition = `transform ${spinDuration}ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`;
    wheel.style.transform = `rotate(${totalRotation}deg)`;
    
    setTimeout(() => {
      // Calculate where the wheel actually stopped
      const finalAngle = totalRotation % 360;
      const normalizedAngle = (360 - finalAngle) % 360;
      const segmentAngle = 360 / 10;
      const segmentIndex = Math.floor(normalizedAngle / segmentAngle);
      
      const landedOnBlue = segmentIndex % 2 === 0;
      const landedColor = landedOnBlue ? "Blue" : "White";
      
      const playerWins = (selectedColor === "blue" && landedOnBlue) || (selectedColor === "white" && !landedOnBlue);
      
      if (playerWins) {
        setBalance(prev => prev + betAmount);
        setLastResult({ 
          result: "WIN", 
          win: true, 
          amount: betAmount,
          color: landedColor,
          segment: segmentIndex + 1,
          chosenColor: selectedColor
        });
      } else {
        setBalance(prev => prev - betAmount);
        setLastResult({ 
          result: "LOSE", 
          win: false, 
          amount: betAmount,
          color: landedColor,
          segment: segmentIndex + 1,
          chosenColor: selectedColor
        });
      }
      
      // Clear transition after spinning is done
      wheel.style.transition = 'none';
      setIsSpinning(false);
      
      // Show result modal with slight delay for better UX
      setTimeout(() => {
        setShowResultModal(true);
      }, 300);
      
    }, spinDuration);
  };

  if (!isMounted) {
    return null;
  }

  return (
    <Protected>
      <div style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        fontFamily: '"Prompt", system-ui, Arial, sans-serif',
        padding: "20px",
        paddingBottom: "40px" // Add extra bottom padding
      }}>
        <AuthenticatedHeader />
        
        <div style={{ textAlign: "center", marginTop: "60px", marginBottom: "40px" }}>
          <h1 style={{ 
            color: "white", 
            fontSize: "3rem", 
            margin: "0 0 16px 0", 
            fontWeight: "900",
            textShadow: "2px 2px 4px rgba(0,0,0,0.5)"
          }}>
            🎯 Wheel of Luck
          </h1>
          <p style={{ 
            color: "rgba(255,255,255,0.9)", 
            fontSize: "1.2rem", 
            margin: 0 
          }}>
            Choose Blue or White and spin for luck!
          </p>
        </div>

        <div style={{ 
          display: "flex", 
          gap: "40px", 
          flexWrap: "wrap",
          maxWidth: "1400px",
          margin: "0 auto",
          justifyContent: "center",
          alignItems: "flex-start" // Align items to top instead of stretch
        }}>
          
          <div style={{
            background: "rgba(255, 255, 255, 0.95)",
            borderRadius: "20px",
            padding: "40px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)",
            backdropFilter: "blur(10px)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "30px",
            minWidth: "600px" // Increased from 500px
          }}>
            
            <div style={{ position: "relative", width: "500px", height: "500px" }}> {/* Increased from 400px */}
              <div style={{
                position: "absolute",
                top: "-5px",
                left: "50%",
                transform: "translateX(-50%) rotate(180deg)",
                width: "0",
                height: "0",
                borderLeft: "18px solid transparent",
                borderRight: "18px solid transparent",
                borderBottom: "35px solid #e53e3e",
                zIndex: 10,
                filter: "drop-shadow(0 2px 4px rgba(255, 0, 0, 0.8))"
              }} />
              
              <div 
                ref={wheelRef}
                style={{
                  width: "500px", // Increased from 400px
                  height: "500px", // Increased from 400px
                  borderRadius: "50%",
                  border: "10px solid #333",
                  position: "relative",
                  overflow: "hidden",
                  transform: "rotate(0deg)",
                  // Remove the transition property from here - it's controlled by JS
                  background: "conic-gradient(from 0deg, #2196F3 0deg 36deg, #ffffff 36deg 72deg, #2196F3 72deg 108deg, #ffffff 108deg 144deg, #2196F3 144deg 180deg, #ffffff 180deg 216deg, #2196F3 216deg 252deg, #ffffff 252deg 288deg, #2196F3 288deg 324deg, #ffffff 324deg 360deg)",
                  boxShadow: "0 15px 40px rgba(0, 0, 0, 0.4)"
                }}
              >
                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((index) => {
                  const angle = index * 36;
                  return (
                    <div
                      key={index}
                      style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        width: "2px",
                        height: "50%",
                        backgroundColor: "#ddd",
                        transformOrigin: "0 0",
                        transform: `rotate(${angle}deg)`
                      }}
                    />
                  );
                })}

                {[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((index) => {
                  const angle = index * 36 + 18;
                  const isBlue = index % 2 === 0;
                  const radius = 140; // Increased from 110
                  const x = Math.cos((angle - 90) * Math.PI / 180) * radius;
                  const y = Math.sin((angle - 90) * Math.PI / 180) * radius;
                  
                  return (
                    <div
                      key={`icon-${index}`}
                      style={{
                        position: "absolute",
                        top: "50%",
                        left: "50%",
                        transform: `translate(${x}px, ${y}px) translate(-50%, -50%)`,
                        fontSize: "32px", // Increased from 28px
                        textShadow: isBlue ? "0 1px 2px rgba(0,0,0,0.3)" : "0 1px 2px rgba(255,255,255,0.8)",
                        zIndex: 2
                      }}
                    >
                      {isBlue ? "🍀" : "💎"}
                    </div>
                  );
                })}
                
                <div style={{
                  position: "absolute",
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  width: "80px", // Increased from 65px
                  height: "80px", // Increased from 65px
                  borderRadius: "50%",
                  background: "linear-gradient(45deg, #333, #555)",
                  border: "4px solid #fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontSize: "28px", // Increased from 22px
                  fontWeight: "bold",
                  zIndex: 5,
                  boxShadow: "0 3px 12px rgba(0,0,0,0.4)"
                }}>
                  🎯
                </div>
              </div>
            </div>

            <div style={{
              display: "flex",
              gap: "15px",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <button
                onClick={() => setSelectedColor("blue")}
                disabled={isSpinning}
                style={{
                  background: selectedColor === "blue" 
                    ? "linear-gradient(45deg, #2196F3, #1976D2)" 
                    : "rgba(33, 150, 243, 0.2)",
                  color: selectedColor === "blue" ? "white" : "#2196F3",
                  border: selectedColor === "blue" ? "none" : "2px solid #2196F3",
                  borderRadius: "15px",
                  padding: "12px 24px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: isSpinning ? "not-allowed" : "pointer",
                  transition: "all 0.3s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  boxShadow: selectedColor === "blue" ? "0 4px 15px rgba(33, 150, 243, 0.4)" : "none"
                }}
              >
                🍀 BLUE
              </button>
              
              <div style={{
                fontSize: "18px",
                fontWeight: "bold",
                color: "#666"
              }}>
                choose
              </div>
              
              <button
                onClick={() => setSelectedColor("white")}
                disabled={isSpinning}
                style={{
                  background: selectedColor === "white" 
                    ? "linear-gradient(45deg, #757575, #424242)" 
                    : "rgba(117, 117, 117, 0.2)",
                  color: selectedColor === "white" ? "white" : "#757575",
                  border: selectedColor === "white" ? "none" : "2px solid #757575",
                  borderRadius: "15px",
                  padding: "12px 24px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: isSpinning ? "not-allowed" : "pointer",
                  transition: "all 0.3s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  boxShadow: selectedColor === "white" ? "0 4px 15px rgba(117, 117, 117, 0.4)" : "none"
                }}
              >
                💎 WHITE
              </button>
            </div>

            <button
              onClick={spinWheel}
              disabled={isSpinning || betAmount > balance || betAmount <= 0}
              style={{
                background: isSpinning ? "#ccc" : "linear-gradient(45deg, #FF6B35, #F7931E)",
                color: "white",
                border: "none",
                borderRadius: "50px",
                padding: "15px 30px",
                fontSize: "18px",
                fontWeight: "bold",
                cursor: isSpinning ? "not-allowed" : "pointer",
                boxShadow: "0 8px 25px rgba(255, 107, 53, 0.3)",
                transform: isSpinning ? "scale(0.95)" : "scale(1)",
                transition: "all 0.2s ease"
              }}
            >
              {isSpinning ? "🎲 SPINNING..." : `🎲 SPIN FOR ${selectedColor.toUpperCase()}`}
            </button>
          </div>

          <div style={{
            width: "500px",
            background: "rgba(255, 255, 255, 0.95)",
            borderRadius: "20px",
            padding: "30px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.3)",
            backdropFilter: "blur(10px)",
            display: "flex",
            flexDirection: "column",
            gap: "20px",
            maxHeight: "calc(100vh - 200px)", // Limit max height to prevent overflow
            overflowY: "auto" // Add scroll if content is too long
          }}>
            
            <div style={{
              background: "linear-gradient(45deg, #4CAF50, #45a049)",
              borderRadius: "15px",
              padding: "20px",
              textAlign: "center",
              color: "white"
            }}>
              <div style={{ fontSize: "14px", opacity: 0.9 }}>Your Balance</div>
              <div style={{ fontSize: "28px", fontWeight: "bold" }}>💰 {balance} coins</div>
            </div>

            <div>
              <label style={{ 
                display: "block", 
                marginBottom: "10px", 
                fontWeight: "bold",
                color: "#333"
              }}>
                Bet Amount
              </label>
              <div style={{ display: "flex", gap: "10px", alignItems: "center", width: "100%" }}>
                <button
                  onClick={() => setBetAmount(Math.max(10, betAmount - 10))}
                  style={{
                    background: "#f44336",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    minWidth: "50px" // Ensure consistent button size
                  }}
                >
                  -10
                </button>
                <input
                  type="number"
                  value={betAmount}
                  onChange={(e) => setBetAmount(Math.max(0, parseInt(e.target.value) || 0))}
                  style={{
                    flex: 1,
                    padding: "10px",
                    border: "2px solid #ddd",
                    borderRadius: "8px",
                    textAlign: "center",
                    fontSize: "16px",
                    maxWidth: "calc(100% - 120px)" // Leave space for buttons
                  }}
                />
                <button
                  onClick={() => setBetAmount(Math.min(balance, betAmount + 10))}
                  style={{
                    background: "#4CAF50",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    minWidth: "50px" // Ensure consistent button size
                  }}
                >
                  +10
                </button>
              </div>
              
              <div style={{ 
                display: "flex", 
                gap: "8px", 
                marginTop: "10px",
                flexWrap: "wrap"
              }}>
                {[25, 50, 100, 250].map(amount => (
                  <button
                    key={amount}
                    onClick={() => setBetAmount(Math.min(balance, amount))}
                    style={{
                      background: betAmount === amount ? "#2196F3" : "#eee",
                      color: betAmount === amount ? "white" : "#333",
                      border: "none",
                      borderRadius: "6px",
                      padding: "6px 12px",
                      cursor: "pointer",
                      fontSize: "12px"
                    }}
                  >
                    {amount}
                  </button>
                ))}
              </div>
            </div>

            <div style={{
              background: "rgba(103, 58, 183, 0.1)",
              borderRadius: "10px",
              padding: "20px" // Increased from 15px
            }}>
              <h4 style={{ margin: "0 0 15px 0", color: "#333", fontSize: "18px" }}>🎯 Game Rules</h4>
              <div style={{ fontSize: "15px", color: "#444", lineHeight: "1.6" }}> {/* Improved readability */}
                <div style={{ marginBottom: "12px", padding: "8px", background: "rgba(33, 150, 243, 0.1)", borderRadius: "6px" }}>
                  <span style={{ color: "#1976D2", fontWeight: "bold", fontSize: "16px" }}>Blue 🍀 (5 segments):</span>
                  <br />
                  <span style={{ color: "#555" }}>Choose blue to win when wheel lands on blue!</span>
                </div>
                <div style={{ marginBottom: "12px", padding: "8px", background: "rgba(117, 117, 117, 0.1)", borderRadius: "6px" }}>
                  <span style={{ color: "#424242", fontWeight: "bold", fontSize: "16px" }}>White 💎 (5 segments):</span>
                  <br />
                  <span style={{ color: "#555" }}>Choose white to win when wheel lands on white!</span>
                </div>
                <div style={{ 
                  marginTop: "15px", 
                  fontSize: "14px", 
                  background: "rgba(255, 193, 7, 0.15)", 
                  padding: "12px", 
                  borderRadius: "8px",
                  border: "1px solid rgba(255, 193, 7, 0.3)"
                }}>
                  <div style={{ fontWeight: "bold", color: "#333", marginBottom: "8px" }}>Your Current Choice:</div>
                  <div style={{ 
                    color: selectedColor === "blue" ? "#1976D2" : "#424242", 
                    fontWeight: "bold",
                    fontSize: "16px",
                    marginBottom: "8px"
                  }}>
                    {selectedColor === "blue" ? "🍀 BLUE" : "💎 WHITE"}
                  </div>
                  <div style={{ color: "#555", fontSize: "13px" }}>
                    Win if wheel lands on your chosen color! • 50/50 chance • 1:1 payout
                  </div>
                </div>
              </div>
            </div>

            {lastResult && (
              <div style={{
                background: lastResult.win ? "rgba(33, 150, 243, 0.12)" : "rgba(244, 67, 54, 0.12)",
                borderRadius: "12px",
                padding: "15px",
                textAlign: "center",
                border: lastResult.win ? "2px solid #2196F3" : "2px solid #f44336",
                marginBottom: "10px"
              }}>
                <div style={{ fontSize: "16px", color: "#555", marginBottom: "8px" }}>
                  Last Result: {/* ← Change this text here */}
                </div>
                <div style={{ 
                  color: lastResult.win ? "#1976D2" : "#f44336",
                  fontWeight: "bold",
                  fontSize: "18px"
                }}>
                  {lastResult.win ? "WIN" : "LOSE"} {lastResult.win ? "+" : "-"}{lastResult.amount} coins
                  {/* ← You can also modify this text format */}
                </div>
              </div>
            )}

            <button
              onClick={() => setBetAmount(balance)}
              style={{
                background: "linear-gradient(45deg, #9C27B0, #673AB7)",
                color: "white",
                border: "none",
                borderRadius: "10px",
                padding: "12px",
                cursor: "pointer",
                fontWeight: "bold"
              }}
            >
              🚀 ALL IN ({balance} coins)
            </button>
          </div>
        </div>
      </div>
      
      {/* Result Modal Popup */}
      {showResultModal && lastResult && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          backgroundColor: "rgba(0, 0, 0, 0.7)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          animation: "fadeIn 0.3s ease-out"
        }}>
          <div style={{
            background: "white",
            borderRadius: "20px",
            padding: "40px",
            textAlign: "center",
            maxWidth: "400px",
            width: "90%",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.4)",
            transform: "scale(1)",
            animation: "popUp 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)"
          }}>
            <div style={{ 
              fontSize: "60px", 
              marginBottom: "20px"
            }}>
              {lastResult.win ? "🎉" : "😞"}
            </div>
            
            <div style={{
              fontSize: "32px",
              fontWeight: "bold",
              color: lastResult.win ? "#4CAF50" : "#f44336",
              marginBottom: "20px"
            }}>
              {lastResult.result}!
            </div>
            
            <div style={{
              fontSize: "18px",
              color: "#555",
              marginBottom: "15px",
              lineHeight: "1.4"
            }}>
              You chose: <span style={{ 
                fontWeight: "bold", 
                color: lastResult.chosenColor === "blue" ? "#2196F3" : "#666"
              }}>
                {lastResult.chosenColor === "blue" ? "🍀 Blue" : "💎 White"}
              </span>
            </div>
            
            <div style={{
              fontSize: "18px",
              color: "#555",
              marginBottom: "25px",
              lineHeight: "1.4"
            }}>
              Wheel landed on: <span style={{ 
                fontWeight: "bold",
                color: lastResult.color === "Blue" ? "#2196F3" : "#666"
              }}>
                {lastResult.color === "Blue" ? "🍀" : "💎"} {lastResult.color}
              </span>
            </div>
            
            <div style={{
              fontSize: "24px",
              fontWeight: "bold",
              color: lastResult.win ? "#4CAF50" : "#f44336",
              marginBottom: "30px",
              padding: "15px",
              background: lastResult.win ? "rgba(76, 175, 80, 0.1)" : "rgba(244, 67, 54, 0.1)",
              borderRadius: "10px",
              border: lastResult.win ? "2px solid #4CAF50" : "2px solid #f44336"
            }}>
              {lastResult.win ? "+" : "-"}{lastResult.amount} coins
            </div>
            
            <button
              onClick={() => setShowResultModal(false)}
              style={{
                background: "linear-gradient(45deg, #2196F3, #1976D2)",
                color: "white",
                border: "none",
                borderRadius: "25px",
                padding: "12px 30px",
                fontSize: "16px",
                fontWeight: "bold",
                cursor: "pointer",
                boxShadow: "0 4px 15px rgba(33, 150, 243, 0.4)",
                transition: "all 0.2s ease"
              }}
              onMouseOver={(e) => e.target.style.transform = "translateY(-2px)"}
              onMouseOut={(e) => e.target.style.transform = "translateY(0px)"}
            >
              Continue Playing
            </button>
          </div>
        </div>
      )}
      
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes popUp {
          0% { 
            opacity: 0;
            transform: scale(0.3) translateY(100px);
          }
          50% {
            opacity: 1;
            transform: scale(1.05) translateY(-10px);
          }
          100% { 
            opacity: 1;
            transform: scale(1) translateY(0px);
          }
        }
      `}</style>
    </Protected>
  );
}
