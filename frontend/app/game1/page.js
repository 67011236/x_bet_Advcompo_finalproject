"use client";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";

export default function Game1() {
  return (
    <Protected>
      <div className="game1-page">
        <AuthenticatedHeader />
        
        <div className="container" style={{ padding: "20px" }}>
          <div className="header">
            <h1>Game 1</h1>
            <p>Welcome to Game 1 - Your gaming experience starts here!</p>
          </div>
          
          <div className="game-content" style={{ 
            display: "flex", 
            flexDirection: "column",
            alignItems: "center",
            gap: "20px",
            marginTop: "30px"
          }}>
            <div className="game-area" style={{
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: "15px",
              padding: "40px",
              textAlign: "center",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)",
              maxWidth: "600px",
              width: "100%"
            }}>
              <h2 style={{ color: "#333", marginBottom: "20px" }}>Game 1 Interface</h2>
              <p style={{ color: "#666", marginBottom: "30px" }}>
                This is where your game logic and interface will go.
              </p>
              
              <div className="game-controls" style={{ display: "flex", gap: "15px", justifyContent: "center" }}>
                <button style={{
                  background: "#667eea",
                  color: "white",
                  border: "none",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "16px"
                }}>
                  Start Game
                </button>
                
                <button style={{
                  background: "#6c757d",
                  color: "white",
                  border: "none",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "16px"
                }}>
                  Rules
                </button>
                
                <button style={{
                  background: "#28a745",
                  color: "white",
                  border: "none",
                  padding: "12px 24px",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "16px"
                }}>
                  High Scores
                </button>
              </div>
            </div>
            
            {/* Game Statistics or Info */}
            <div className="game-stats" style={{
              background: "rgba(255, 255, 255, 0.8)",
              borderRadius: "10px",
              padding: "20px",
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
              gap: "15px",
              maxWidth: "600px",
              width: "100%"
            }}>
              <div style={{ textAlign: "center" }}>
                <h4 style={{ color: "#333", margin: "0 0 5px 0" }}>Score</h4>
                <p style={{ color: "#666", margin: 0, fontSize: "18px", fontWeight: "bold" }}>0</p>
              </div>
              <div style={{ textAlign: "center" }}>
                <h4 style={{ color: "#333", margin: "0 0 5px 0" }}>Level</h4>
                <p style={{ color: "#666", margin: 0, fontSize: "18px", fontWeight: "bold" }}>1</p>
              </div>
              <div style={{ textAlign: "center" }}>
                <h4 style={{ color: "#333", margin: "0 0 5px 0" }}>Lives</h4>
                <p style={{ color: "#666", margin: 0, fontSize: "18px", fontWeight: "bold" }}>3</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Protected>
  );
}