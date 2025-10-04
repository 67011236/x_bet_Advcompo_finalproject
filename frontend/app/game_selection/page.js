"use client";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";

export default function GameSelection() {
  return (
    <Protected>
      <div className="game-selection">
        <AuthenticatedHeader />
        
        <div className="container" style={{ padding: "20px" }}>
          <div className="header">
            <h1>Game Selection</h1>
            <p>Choose your favorite games to play</p>
          </div>
          
          <div className="games-grid" style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", 
            gap: "20px",
            marginTop: "30px"
          }}>
            <div className="game-card" style={{
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: "15px",
              padding: "25px",
              textAlign: "center",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
            }}>
              <h3>Sports Betting</h3>
              <p>Bet on your favorite sports</p>
              <button style={{
                background: "#667eea",
                color: "white",
                border: "none",
                padding: "10px 20px",
                borderRadius: "8px",
                cursor: "pointer"
              }}>Play Now</button>
            </div>
            
            <div className="game-card" style={{
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: "15px",
              padding: "25px",
              textAlign: "center",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
            }}>
              <h3>Casino Games</h3>
              <p>Try your luck with casino games</p>
              <button style={{
                background: "#667eea",
                color: "white",
                border: "none",
                padding: "10px 20px",
                borderRadius: "8px",
                cursor: "pointer"
              }}>Play Now</button>
            </div>
            
            <div className="game-card" style={{
              background: "rgba(255, 255, 255, 0.9)",
              borderRadius: "15px",
              padding: "25px",
              textAlign: "center",
              boxShadow: "0 8px 32px rgba(0, 0, 0, 0.1)"
            }}>
              <h3>Live Games</h3>
              <p>Play with real dealers</p>
              <button style={{
                background: "#667eea",
                color: "white",
                border: "none",
                padding: "10px 20px",
                borderRadius: "8px",
                cursor: "pointer"
              }}>Play Now</button>
            </div>
          </div>
        </div>
      </div>
    </Protected>
  );
}