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

  const currency = "THB";
  const fee = "0.00";

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
      alert("Please agree to Terms of Service and Privacy Policy");
      return;
    }
    
    const amount = parseFloat(withdrawAmount);
    if (amount <= 0) {
      alert("Please enter a valid amount");
      return;
    }

    if (amount > parseFloat(balance)) {
      alert("Insufficient balance");
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
        alert(`Withdrawal successful! New balance: ${data.new_balance.toFixed(2)} ${currency}`);
        setBalance(data.new_balance.toFixed(2));
        setWithdrawAmount("");
        setWithdrawAgree(false);
      } else {
        alert(data.detail || "Withdrawal failed");
      }
    } catch (error) {
      console.error("Withdraw error:", error);
      alert("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDeposit = async (e) => {
    e.preventDefault();
    if (!depositAgree) {
      alert("Please agree to Terms of Service and Privacy Policy");
      return;
    }
    
    const amount = parseFloat(depositAmount);
    if (amount <= 0) {
      alert("Please enter a valid amount");
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
        alert(`Deposit successful! New balance: ${data.new_balance.toFixed(2)} ${currency}`);
        setBalance(data.new_balance.toFixed(2));
        setDepositAmount("");
        setDepositAgree(false);
      } else {
        alert(data.detail || "Deposit failed");
      }
    } catch (error) {
      console.error("Deposit error:", error);
      alert("Network error. Please try again.");
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
    </Protected>
  );
}
