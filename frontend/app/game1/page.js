"use client";
import { useState, useEffect, useRef } from "react";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "./style.css";

export default function Game1() {
  const [balance, setBalance] = useState(0);
  const [betAmount, setBetAmount] = useState(50);
  const [lastResult, setLastResult] = useState(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedColor, setSelectedColor] = useState("blue");
  const [isMounted, setIsMounted] = useState(false);
  const [showResultModal, setShowResultModal] = useState(false);
  const wheelRef = useRef(null);

  useEffect(() => {
    setIsMounted(true);
    fetchBalance();
  }, []);

  const fetchBalance = async () => {
    try {
      const response = await fetch("http://localhost:8000/balance", {
        method: "GET",
        credentials: "include",
      });
      
      if (response.ok) {
        const data = await response.json();
        setBalance(data.amount);
      } else {
        console.error("Failed to fetch balance");
      }
    } catch (error) {
      console.error("Error fetching balance:", error);
    }
  };

  const updateBalance = async (newAmount) => {
    try {
      // อัพเดต balance ใน state ทันที
      setBalance(newAmount);
      
      // เรียก API เพื่อ sync กับ database
      await fetchBalance();
    } catch (error) {
      console.error("Error updating balance:", error);
    }
  };

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const spinWheel = async () => {
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
    
    setTimeout(async () => {
      // Calculate where the wheel actually stopped
      const finalAngle = totalRotation % 360;
      const normalizedAngle = (360 - finalAngle) % 360;
      const segmentAngle = 360 / 10;
      const segmentIndex = Math.floor(normalizedAngle / segmentAngle);
      
      const landedOnBlue = segmentIndex % 2 === 0;
      const landedColor = landedOnBlue ? "Blue" : "White";
      
      const playerWins = (selectedColor === "blue" && landedOnBlue) || (selectedColor === "white" && !landedOnBlue);
      
      // Prepare game result for API call
      const gameResult = {
        game_type: "wheel",
        result: playerWins ? "win" : "lose",
        bet_amount: betAmount,
        win_amount: playerWins ? betAmount * 2 : 0
      };

      try {
        // Send game result to backend
        const response = await fetch("http://localhost:8000/api/game-result", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify(gameResult),
        });

        if (response.ok) {
          const data = await response.json();
          // Update balance from backend response
          setBalance(data.new_balance);
          
          setLastResult({ 
            result: playerWins ? "WIN" : "LOSE", 
            win: playerWins, 
            amount: betAmount,
            color: landedColor,
            segment: segmentIndex + 1,
            chosenColor: selectedColor,
            balanceChange: data.balance_change
          });

          // Record game1 play data
          try {
            const game1PlayData = {
              bet_amount: betAmount,
              selected_color: selectedColor,
              result_color: landedOnBlue ? "blue" : "white"
            };

            const game1Response = await fetch("http://localhost:8000/api/game1/play", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              credentials: "include",
              body: JSON.stringify(game1PlayData),
            });

            if (game1Response.ok) {
              console.log("🎮 Game1 play data recorded successfully");
            } else {
              console.warn("⚠️ Failed to record game1 play data");
            }
          } catch (game1Error) {
            console.error("❌ Error recording game1 play:", game1Error);
          }
        } else {
          console.error("Failed to process game result");
          // Fallback to local balance update (original logic)
          if (playerWins) {
            setBalance(prev => prev + betAmount);
          } else {
            setBalance(prev => prev - betAmount);
          }
          
          setLastResult({ 
            result: playerWins ? "WIN" : "LOSE", 
            win: playerWins, 
            amount: betAmount,
            color: landedColor,
            segment: segmentIndex + 1,
            chosenColor: selectedColor
          });
        }
      } catch (error) {
        console.error("Error processing game result:", error);
        // Fallback to local balance update
        if (playerWins) {
          setBalance(prev => prev + betAmount);
        } else {
          setBalance(prev => prev - betAmount);
        }
        
        setLastResult({ 
          result: playerWins ? "WIN" : "LOSE", 
          win: playerWins, 
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
        background: "url('/bg.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundAttachment: "fixed",
        fontFamily: '"Prompt", system-ui, Arial, sans-serif',
        padding: "20px",
        paddingBottom: "40px" // Add extra bottom padding
      }}>
        <AuthenticatedHeader />
        
        <div style={{ textAlign: "center", marginTop: "20px", marginBottom: "20px" }}>
          <h1 style={{ 
            color: "white", 
            fontSize: "2rem", 
            margin: "0 0 8px 0", 
            fontWeight: "900",
            textShadow: "2px 2px 4px rgba(0,0,0,0.5)"
          }}>
            🎯 Wheel of Luck
          </h1>
          <p style={{ 
            color: "rgba(255,255,255,0.9)", 
            fontSize: "1rem", 
            margin: 0 
          }}>
            Choose Blue or White and spin for luck!
          </p>
        </div>

        <div style={{ 
          display: "flex", 
          gap: "20px", 
          flexWrap: "wrap",
          maxWidth: "1200px",
          margin: "0 auto",
          justifyContent: "center",
          alignItems: "center"
        }}>
          
          {/* Game Rules - Left Side */}
          <div style={{
            width: "350px",
            background: "rgba(7, 12, 26, 0.95)",
            borderRadius: "20px",
            padding: "20px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(15px)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            display: "flex",
            flexDirection: "column",
            gap: "15px",
            maxHeight: "calc(100vh - 150px)",
            overflowY: "auto",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            transform: "translateY(0px)",
            cursor: "pointer"
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = "translateY(-8px)";
            e.target.style.boxShadow = "0 25px 80px rgba(0, 0, 0, 0.5), 0 0 30px rgba(113, 221, 255, 0.3)";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "translateY(0px)";
            e.target.style.boxShadow = "0 20px 60px rgba(0, 0, 0, 0.4)";
          }}
          >
            <div style={{
              background: "rgba(0, 90, 255, 0.15)",
              borderRadius: "10px",
              padding: "20px"
            }}>
              <h4 style={{ margin: "0 0 15px 0", color: "#71ddff", fontSize: "18px" }}>🎯 Game Rules</h4>
              <div style={{ fontSize: "15px", color: "#e2e8f0", lineHeight: "1.6" }}>
                <div style={{ 
                  marginBottom: "12px", 
                  padding: "8px", 
                  background: "rgba(33, 150, 243, 0.2)", 
                  borderRadius: "6px",
                  transition: "all 0.3s ease",
                  cursor: "pointer"
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = "translateY(-4px)";
                  e.target.style.background = "rgba(33, 150, 243, 0.35)";
                  e.target.style.boxShadow = "0 8px 20px rgba(33, 150, 243, 0.3)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = "translateY(0px)";
                  e.target.style.background = "rgba(33, 150, 243, 0.2)";
                  e.target.style.boxShadow = "none";
                }}
                >
                  <span style={{ color: "#71ddff", fontWeight: "bold", fontSize: "16px" }}>Blue 🍀 (5 segments):</span>
                  <br />
                  <span style={{ color: "#cbd5e0" }}>Choose blue to win when wheel lands on blue!</span>
                </div>
                <div style={{ 
                  marginBottom: "12px", 
                  padding: "8px", 
                  background: "rgba(255, 255, 255, 0.1)", 
                  borderRadius: "6px",
                  transition: "all 0.3s ease",
                  cursor: "pointer"
                }}
                onMouseEnter={(e) => {
                  e.target.style.transform = "translateY(-4px)";
                  e.target.style.background = "rgba(255, 255, 255, 0.2)";
                  e.target.style.boxShadow = "0 8px 20px rgba(255, 255, 255, 0.2)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = "translateY(0px)";
                  e.target.style.background = "rgba(255, 255, 255, 0.1)";
                  e.target.style.boxShadow = "none";
                }}
                >
                  <span style={{ color: "#f7fafc", fontWeight: "bold", fontSize: "16px" }}>White 💎 (5 segments):</span>
                  <br />
                  <span style={{ color: "#cbd5e0" }}>Choose white to win when wheel lands on white!</span>
                </div>
                <div
                  style={{ 
                    marginTop: "15px", 
                    fontSize: "14px", 
                    background: "rgba(255, 146, 51, 0.18)", 
                    padding: "16px 18px", 
                    borderRadius: "12px",
                    transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    cursor: "pointer"
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.transform = "translateY(-8px)";
                    e.currentTarget.style.boxShadow = "0 12px 32px rgba(255,146,51,0.25)";
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = "translateY(0px)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                >
                  <div style={{ fontWeight: "bold", color: "#ff9233", marginBottom: "8px" }}>Your Current Choice:</div>
                  <span style={{ 
                    color: selectedColor === "blue" ? "#71ddff" : "#f7fafc", 
                    fontWeight: "bold",
                    fontSize: "16px",
                    marginBottom: "8px",
                    display: "block"
                  }}>
                    {selectedColor === "blue" ? "🍀 BLUE" : "💎 WHITE"}
                  </span>
                  <div style={{ color: "#cbd5e0", fontSize: "13px", marginTop: "8px" }}>
                    Win if wheel lands on your chosen color! • 50/50 chance • 1:1 payout
                  </div>
                </div>
              </div>
            </div>

            {lastResult && (
              <div style={{
                background: lastResult.win ? "rgba(0, 90, 255, 0.2)" : "rgba(255, 80, 80, 0.2)",
                borderRadius: "12px",
                padding: "15px",
                textAlign: "center",
                border: lastResult.win ? "2px solid #71ddff" : "2px solid #ff5050",
                marginBottom: "10px"
              }}>
                <div style={{ fontSize: "16px", color: "#cbd5e0", marginBottom: "8px" }}>
                  Last Result:
                </div>
                <div style={{ 
                  color: lastResult.win ? "#71ddff" : "#ff5050",
                  fontWeight: "bold",
                  fontSize: "18px"
                }}>
                  {lastResult.win ? "WIN" : "LOSE"} {lastResult.win ? "+" : "-"}{lastResult.amount} coins
                </div>
              </div>
            )}
          </div>

          {/* Wheel Game - Center */}
          <div style={{
            background: "rgba(7, 12, 26, 0.95)",
            borderRadius: "20px",
            padding: "25px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(15px)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "20px",
            minWidth: "450px"
          }}>
            
            <div style={{ position: "relative", width: "350px", height: "350px" }}>
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
                  width: "350px",
                  height: "350px",
                  borderRadius: "50%",
                  border: "8px solid #333",
                  position: "relative",
                  overflow: "hidden",
                  transform: "rotate(0deg)",
                  // Remove the transition property from here - it's controlled by JS
                  background: "conic-gradient(from 0deg, #2196F3 0deg 36deg, #ffffff 36deg 72deg, #2196F3 72deg 108deg, #ffffff 108deg 144deg, #2196F3 144deg 180deg, #ffffff 180deg 216deg, #2196F3 216deg 252deg, #ffffff 252deg 288deg, #2196F3 288deg 324deg, #ffffff 324deg 360deg)",
                  boxShadow: "0 10px 30px rgba(0, 0, 0, 0.4)"
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
                  const radius = 100;
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
                        fontSize: "24px",
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
                  width: "60px",
                  height: "60px",
                  borderRadius: "50%",
                  background: "linear-gradient(45deg, #333, #555)",
                  border: "3px solid #fff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  color: "white",
                  fontSize: "20px",
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
                    ? "linear-gradient(45deg, #005aff, #0040cc)" 
                    : "rgba(0, 90, 255, 0.2)",
                  color: selectedColor === "blue" ? "white" : "#71ddff",
                  border: selectedColor === "blue" ? "none" : "2px solid #71ddff",
                  borderRadius: "15px",
                  padding: "12px 24px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: isSpinning ? "not-allowed" : "pointer",
                  transition: "all 0.3s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  boxShadow: selectedColor === "blue" ? "0 4px 15px rgba(0, 90, 255, 0.4)" : "none"
                }}
              >
                🍀 BLUE
              </button>
              
              <div style={{
                fontSize: "18px",
                fontWeight: "bold",
                color: "#cbd5e0"
              }}>
                choose
              </div>
              
              <button
                onClick={() => setSelectedColor("white")}
                disabled={isSpinning}
                style={{
                  background: selectedColor === "white" 
                    ? "linear-gradient(45deg, #ffffff, #f8f9fa)" 
                    : "rgba(255, 255, 255, 0.15)",
                  color: selectedColor === "white" ? "#1a202c" : "#f7fafc",
                  border: selectedColor === "white" ? "2px solid #e2e8f0" : "2px solid #f7fafc",
                  borderRadius: "15px",
                  padding: "12px 24px",
                  fontSize: "16px",
                  fontWeight: "bold",
                  cursor: isSpinning ? "not-allowed" : "pointer",
                  transition: "all 0.3s ease",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  boxShadow: selectedColor === "white" ? "0 4px 15px rgba(255, 255, 255, 0.3)" : "none"
                }}
              >
                💎 WHITE
              </button>
            </div>

            <button
              onClick={spinWheel}
              disabled={isSpinning || betAmount > balance || betAmount <= 0}
              style={{
                background: isSpinning ? "#374151" : "linear-gradient(135deg, rgba(113, 221, 255, 0.6) 0%, rgba(0, 144, 255, 0.7) 100%)",
                color: "white",
                border: "none",
                borderRadius: "50px",
                padding: "15px 30px",
                fontSize: "18px",
                fontWeight: "bold",
                cursor: isSpinning ? "not-allowed" : "pointer",
                boxShadow: "0 8px 25px rgba(113, 221, 255, 0.3)",
                transform: isSpinning ? "scale(0.95)" : "scale(1)",
                transition: "all 0.3s ease"
              }}
              onMouseEnter={(e) => {
                if (!isSpinning && betAmount <= balance && betAmount > 0) {
                  e.target.style.background = "linear-gradient(135deg, #71ddff 0%, #0090ff 100%)";
                  e.target.style.transform = "scale(1.05)";
                  e.target.style.boxShadow = "0 12px 35px rgba(113, 221, 255, 0.5)";
                }
              }}
              onMouseLeave={(e) => {
                if (!isSpinning && betAmount <= balance && betAmount > 0) {
                  e.target.style.background = "linear-gradient(135deg, rgba(113, 221, 255, 0.6) 0%, rgba(0, 144, 255, 0.7) 100%)";
                  e.target.style.transform = "scale(1)";
                  e.target.style.boxShadow = "0 8px 25px rgba(113, 221, 255, 0.3)";
                }
              }}
            >
              {isSpinning ? "🎲 SPINNING..." : `🎲 SPIN FOR ${selectedColor.toUpperCase()}`}
            </button>
          </div>

          {/* Balance and Controls - Right Side */}
          <div style={{
            width: "300px",
            background: "rgba(7, 12, 26, 0.95)",
            borderRadius: "20px",
            padding: "20px",
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(15px)",
            border: "1px solid rgba(255, 255, 255, 0.1)",
            display: "flex",
            flexDirection: "column",
            gap: "15px",
            maxHeight: "calc(100vh - 150px)",
            overflowY: "auto",
            transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            transform: "translateY(0px)",
            cursor: "pointer"
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = "translateY(-8px)";
            e.target.style.boxShadow = "0 25px 80px rgba(0, 0, 0, 0.5), 0 0 30px rgba(113, 221, 255, 0.3)";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "translateY(0px)";
            e.target.style.boxShadow = "0 20px 60px rgba(0, 0, 0, 0.4)";
          }}
          >
            
            <div style={{
              background: "linear-gradient(45deg, #ff9233, #ff7a00)",
              borderRadius: "15px",
              padding: "15px",
              textAlign: "center",
              color: "white"
            }}>
              <div style={{ fontSize: "12px", opacity: 0.9 }}>Your Balance</div>
              <div style={{ fontSize: "22px", fontWeight: "bold" }}>💰 {balance} coins</div>
            </div>

            <div>
              <label style={{ 
                display: "block", 
                marginBottom: "10px", 
                fontWeight: "bold",
                color: "#e2e8f0"
              }}>
                Bet Amount
              </label>
              <div style={{ display: "flex", gap: "10px", alignItems: "center", width: "100%" }}>
                <button
                  onClick={() => setBetAmount(Math.max(10, betAmount - 10))}
                  style={{
                    background: "#ff5050",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    minWidth: "50px"
                  }}
                >
                  -10
                </button>
                <input
                  type="number"
                  value={betAmount}
                  onChange={(e) => setBetAmount(Math.max(0, Math.min(balance, parseInt(e.target.value) || 0)))}
                  style={{
                    flex: 1,
                    padding: "10px",
                    border: "2px solid rgba(255, 255, 255, 0.2)",
                    borderRadius: "8px",
                    textAlign: "center",
                    fontSize: "16px",
                    maxWidth: "calc(100% - 120px)",
                    background: "rgba(255, 255, 255, 0.1)",
                    color: "white"
                  }}
                />
                <button
                  onClick={() => setBetAmount(Math.min(balance, betAmount + 10))}
                  style={{
                    background: "#00c851",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 12px",
                    cursor: "pointer",
                    minWidth: "50px"
                  }}
                >
                  +10
                </button>
              </div>
              
              <div style={{ 
                display: "flex", 
                gap: "8px", 
                marginTop: "10px",
                flexWrap: "wrap",
                justifyContent: "center"
              }}>
                {[25, 50, 100].map(amount => (
                  <button
                    key={amount}
                    onClick={() => setBetAmount(Math.min(balance, amount))}
                    style={{
                      background: betAmount === amount ? "#005aff" : "rgba(255, 255, 255, 0.1)",
                      color: betAmount === amount ? "white" : "#e2e8f0",
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

            <button
              onClick={() => setBetAmount(balance)}
              disabled={balance <= 0}
              style={{
                background: balance <= 0 ? "#6b7280" : "linear-gradient(135deg, rgba(113, 221, 255, 0.6) 0%, rgba(0, 144, 255, 0.7) 100%)",
                color: "white",
                border: "none",
                borderRadius: "10px",
                padding: "12px",
                cursor: balance <= 0 ? "not-allowed" : "pointer",
                fontWeight: "bold",
                opacity: balance <= 0 ? 0.5 : 1,
                transition: "all 0.3s ease"
              }}
              onMouseEnter={(e) => {
                if (balance > 0) {
                  e.target.style.background = "linear-gradient(135deg, #71ddff 0%, #0090ff 100%)";
                  e.target.style.transform = "scale(1.05)";
                  e.target.style.boxShadow = "0 8px 20px rgba(113, 221, 255, 0.4)";
                }
              }}
              onMouseLeave={(e) => {
                if (balance > 0) {
                  e.target.style.background = "linear-gradient(135deg, rgba(113, 221, 255, 0.6) 0%, rgba(0, 144, 255, 0.7) 100%)";
                  e.target.style.transform = "scale(1)";
                  e.target.style.boxShadow = "none";
                }
              }}
            >
              🚀 ALL IN ({Math.floor(balance)} coins)
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
