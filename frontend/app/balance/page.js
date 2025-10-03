"use client";
import { useState } from "react";
import SiteHeader from "../../components/SiteHeader";
import "../../styles/balance.css";

export default function BalancePage() {
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawAgree, setWithdrawAgree] = useState(false);
  const [depositAgree, setDepositAgree] = useState(false);
  const [loading, setLoading] = useState(false);

  // Mock balance data
  const balance = "0.00";
  const currency = "THB";
  const fee = "0.00";

  const handleWithdraw = async (e) => {
    e.preventDefault();
    if (!withdrawAgree) {
      alert("Please agree to Terms of Service and Privacy Policy");
      return;
    }
    setLoading(true);
    
    // TODO: Implement withdraw logic
    console.log("Withdraw:", withdrawAmount);
    
    setTimeout(() => {
      setLoading(false);
      alert("Withdraw request submitted");
    }, 1000);
  };

  const handleDeposit = async (e) => {
    e.preventDefault();
    if (!depositAgree) {
      alert("Please agree to Terms of Service and Privacy Policy");
      return;
    }
    setLoading(true);
    
    // TODO: Implement deposit logic
    console.log("Deposit:", depositAmount);
    
    setTimeout(() => {
      setLoading(false);
      alert("Deposit request submitted");
    }, 1000);
  };

  return (
    <div className="balance-page">
      {/* Header */}
      <SiteHeader />

      <div className="balance-container">
        {/* Combined Header and Balance */}
        <div>
          <div className="balance-header">
            <h1>WITHDRAW / DEPOSIT</h1>
          </div>
          <div className="balance-display">
            <h2>Balance</h2>
            <div className="balance-amount">{balance} {currency}</div>
            <div className="balance-status">Available</div>
          </div>
        </div>

        {/* Action Cards */}
        <div className="action-grid">
          {/* Withdraw Card */}
          <div className="action-card">
            <h3>Withdraw</h3>
            
            <div className="warning-banner">
              Please carefully check your transaction details
            </div>

            <form onSubmit={handleWithdraw}>
              <div className="form-group">
                <label className="form-label">Enter Amount</label>
                <input
                  type="number"
                  className="form-input"
                  value={withdrawAmount}
                  onChange={(e) => setWithdrawAmount(e.target.value)}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="fee-display">
                Fee<br />
                {fee} {currency}
              </div>

              <button 
                type="submit" 
                className="action-btn"
                disabled={loading || !withdrawAmount || !withdrawAgree}
              >
                {loading ? "Processing..." : "Confirm"}
              </button>

              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="withdrawAgree"
                  checked={withdrawAgree}
                  onChange={(e) => setWithdrawAgree(e.target.checked)}
                  required
                />
                <label htmlFor="withdrawAgree">
                  I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                </label>
              </div>
            </form>
          </div>

          {/* Deposit Card */}
          <div className="action-card">
            <h3>Deposit</h3>
            
            <div className="warning-banner">
              Please carefully check your transaction details
            </div>

            <form onSubmit={handleDeposit}>
              <div className="form-group">
                <label className="form-label">Enter Amount</label>
                <input
                  type="number"
                  className="form-input"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  placeholder="0.00"
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="fee-display">
                Fee<br />
                {fee} {currency}
              </div>

              <button 
                type="submit" 
                className="action-btn"
                disabled={loading || !depositAmount || !depositAgree}
              >
                {loading ? "Processing..." : "Confirm"}
              </button>

              <div className="checkbox-group">
                <input
                  type="checkbox"
                  id="depositAgree"
                  checked={depositAgree}
                  onChange={(e) => setDepositAgree(e.target.checked)}
                  required
                />
                <label htmlFor="depositAgree">
                  I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                </label>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
