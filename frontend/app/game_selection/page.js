"use client";
import Link from "next/link";
import Protected from "../../components/Protected";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "../../styles/game-selection.css";

export default function GameSelection() {
  // Mouse tracking wave effect
  const handleMouseMove = (event) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    
    // Update CSS custom properties for the wave position (เป็น percentage)
    button.style.setProperty('--mouse-x', `${x}%`);
    button.style.setProperty('--mouse-y', `${y}%`);
  };

  const handleMouseEnter = (event) => {
    const button = event.currentTarget;
    // เพิ่ม class สำหรับ active wave state
    button.classList.add('wave-active');
  };

  const handleMouseLeave = (event) => {
    const button = event.currentTarget;
    // Reset position to center when mouse leaves
    button.style.setProperty('--mouse-x', '50%');
    button.style.setProperty('--mouse-y', '50%');
    button.classList.remove('wave-active');
  };
  return (
    <Protected>
      <div className="game-selection-page">
        <AuthenticatedHeader />
        
        <div className="game-container">
          {/* Header */}
          <div className="game-header">
            <h1>Game selection</h1>
          </div>

          {/* Subtitle */}
          <div className="game-subtitle">
            <p>One click to instant outcomes transparent and fast, with risk fully under your control.</p>
          </div>

          {/* Games Grid */}
          <div className="games-grid">
            {/* Premium Wheel Card */}
            <div className="game-card">
              <h2>Premium Wheel</h2>
              <div className="game-description">
                <h3>Description</h3>
                <ul>
                  <li>One spin, total payout up to 2x your stake</li>
                  <li>Fast, concise, transparent — Blue pays 2x, White loses stake</li>
                </ul>
              </div>
              <Link href="/game1">
                <button 
                  className="game-btn"
                  onMouseMove={handleMouseMove}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Spin in style
                </button>
              </Link>
            </div>

            {/* Rock-Paper-Scissors Card */}
            <div className="game-card">
              <h2>Rock-Paper-Scissors</h2>
              <div className="game-description">
                <h3>Description</h3>
                <ul>
                  <li>Head-to-head strategy. Quick rounds, clear results.</li>
                  <li>Choose precisely, read your opponent, and close it out clean.</li>
                  <li>Rapid duel mode - Easy on the eyes</li>
                </ul>
              </div>
              <Link href="/game2">
                <button 
                  className="game-btn"
                  onMouseMove={handleMouseMove}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
                >
                  Duel Now
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Protected>
  );
}