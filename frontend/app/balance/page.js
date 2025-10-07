"use client";
import { useState, useEffect } from "react";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import Protected from "../../components/Protected";
import "../../styles/balance.css";

export default function BalancePage() {
  const [withdrawAmount, setWithdrawAmount] = useState("");
  const [depositAmount, setDepositAmount] = useState("");
  const [withdrawAgree, setWithdrawAgree] = useState(false);
  const [depositAgree, setDepositAgree] = useState(false);
  const [loading, setLoading] = useState(false);
  const [balance, setBalance] = useState("0.00");
  const [balanceLoading, setBalanceLoading] = useState(true);
  const [notification, setNotification] = useState(null);

  const currency = "THB";
  const fee = "0.00";

  // Show notification function
  const showNotification = (message, type) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

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

  // Fetch balance when component mounts
  useEffect(() => {
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
        setBalance(data.amount.toFixed(2));
      } else {
        console.error("Failed to fetch balance");
      }
    } catch (error) {
      console.error("Error fetching balance:", error);
    } finally {
      setBalanceLoading(false);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    if (!withdrawAgree) {
      showNotification("Please agree to Terms of Service and Privacy Policy", 'error');
      return;
    }
    
    const amount = parseFloat(withdrawAmount);
    if (amount <= 0) {
      showNotification("Please enter a valid amount", 'error');
      return;
    }

    if (amount > parseFloat(balance)) {
      showNotification("Insufficient balance", 'error');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:8000/withdraw", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ amount: amount }),
      });

      const data = await response.json();

      if (response.ok) {
        showNotification(`Withdrawal successful! New balance: ${data.new_balance.toFixed(2)} ${currency}`, 'error');
        setBalance(data.new_balance.toFixed(2));
        setWithdrawAmount("");
        setWithdrawAgree(false);
      } else {
        showNotification(data.detail || "Withdrawal failed", 'error');
      }
    } catch (error) {
      console.error("Withdraw error:", error);
      showNotification("Network error. Please try again.", 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeposit = async (e) => {
    e.preventDefault();
    if (!depositAgree) {
      showNotification("Please agree to Terms of Service and Privacy Policy", 'error');
      return;
    }
    
    const amount = parseFloat(depositAmount);
    if (amount <= 0) {
      showNotification("Please enter a valid amount", 'error');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch("http://localhost:8000/deposit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ amount: amount }),
      });

      const data = await response.json();

      if (response.ok) {
        showNotification(`Deposit successful! New balance: ${data.new_balance.toFixed(2)} ${currency}`, 'success');
        setBalance(data.new_balance.toFixed(2));
        setDepositAmount("");
        setDepositAgree(false);
      } else {
        showNotification(data.detail || "Deposit failed", 'error');
      }
    } catch (error) {
      console.error("Deposit error:", error);
      showNotification("Network error. Please try again.", 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Protected>
      <div className="balance-page">
        {/* Header */}
        <AuthenticatedHeader />

        <div className="balance-container">
          {/* Combined Header and Balance */}
          <div>
            <div className="balance-header">
              <h1>WITHDRAW / DEPOSIT</h1>
            </div>
            <div className="balance-display">
              <h2>Balance</h2>
              <div className="balance-amount">
                {balanceLoading ? "Loading..." : `${balance} ${currency}`}
              </div>
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
                onMouseMove={handleMouseMove}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
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
                onMouseMove={handleMouseMove}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
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

      {/* Notification */}
      {notification && (
        <div className={`notification ${notification.type}`}>
          <div className="notification-content">
            <span>{notification.message}</span>
            <button 
              className="notification-close" 
              onClick={() => setNotification(null)}
            >
              ×
            </button>
          </div>
        </div>
      )}
      </div>
    </Protected>
  );
}
