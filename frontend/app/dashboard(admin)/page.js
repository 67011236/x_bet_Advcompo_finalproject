"use client";
import { useState, useEffect } from "react";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import Protected from "../../components/Protected";
import Adminonly from "../../components/Adminonly";
import "../../styles/dashboard.css";

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalReports: 0,
    totalBalance: 500000,
  });

  const [gameStats, setGameStats] = useState([
    { name: "Premium Wheel", percentage: 60, color: "#71ddff" },
    { name: "Rock-Paper-Scissors", percentage: 40, color: "#4a9eff" }
  ]);

  const [realtimeActivities, setRealtimeActivities] = useState([
    { id: "Test1234@gmail.com", amount: "100000.00 THB", type: "win", time: "2m ago" },
    { id: "Test1234@gmail.com", amount: "50.00 THB", type: "loss", time: "5m ago" },
    { id: "Test1234@gmail.com", amount: "100000.00 THB", type: "win", time: "8m ago" },
    { id: "Test1234@gmail.com", amount: "50.00 THB", type: "loss", time: "12m ago" },
    { id: "Test1234@gmail.com", amount: "50.00 THB", type: "loss", time: "15m ago" }
  ]);

  const incomeData = [
    { month: "Jan", value: 80 },
    { month: "Feb", value: 80 },
    { month: "Mar", value: 80 },
    { month: "Apr", value: 80 },
    { month: "May", value: 80 }
  ];

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/dashboard-stats", {
        credentials: 'include'
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats({
          totalUsers: data.total_users,
          totalReports: data.total_reports,
          totalBalance: 500000,
        });
      } else {
        console.error("Failed to fetch dashboard stats");
      }
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
    
    // Set up interval to refresh stats every 10 seconds
    const interval = setInterval(fetchDashboardStats, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <Protected>
      <Adminonly>
        <div className="admin-dashboard">
          <AuthenticatedHeader />
          
          <div className="dashboard-container">
            {/* Header */}
            <div className="dashboard-header">
              <h1>Dashboard</h1>
            </div>
            
            {/* Top Stats */}
            <div className="top-stats">
              <div className="stat-card">
                <h3>Total User</h3>
                <div className="stat-value">{stats.totalUsers} User</div>
              </div>
              
              <div className="stat-card">
                <h3>Total reports</h3>
                <div className="stat-value">{stats.totalReports} Reports</div>
              </div>
              
              <div className="stat-card chart-card">
                <h3>More players</h3>
                <div className="chart-container">
                  <div className="donut-chart">
                    <svg width="120" height="120" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="40"
                        fill="none"
                        stroke="#71ddff"
                        strokeWidth="15"
                        strokeDasharray={`${gameStats[0].percentage * 2.51} 251`}
                        strokeDashoffset="0"
                        transform="rotate(-90 60 60)"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="40"
                        fill="none"
                        stroke="#4a9eff"
                        strokeWidth="15"
                        strokeDasharray={`${gameStats[1].percentage * 2.51} 251`}
                        strokeDashoffset={`-${gameStats[0].percentage * 2.51}`}
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                  </div>
                  <div className="chart-legend">
                    {gameStats.map((game, index) => (
                      <div key={index} className="legend-item">
                        <span className="legend-color" style={{backgroundColor: game.color}}></span>
                        <span className="legend-text">{game.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Grid */}
            <div className="bottom-grid">
              {/* Income Chart */}
              <div className="chart-card-large">
                <h3>Income</h3>
                <div className="bar-chart">
                  {incomeData.map((item, index) => (
                    <div key={index} className="bar-container">
                      <div 
                        className="bar" 
                        style={{height: `${item.value}%`}}
                      ></div>
                      <span className="bar-label">{item.month}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Real time activities */}
              <div className="realtime-card">
                <h3>Real time</h3>
                <div className="activity-list">
                  {realtimeActivities.map((activity, index) => (
                    <div key={index} className="activity-item">
                      <div className="activity-user">
                        <span className="user-indicator" style={{
                          backgroundColor: activity.type === 'win' ? '#71ddff' : '#4a9eff'
                        }}></span>
                        <span className="user-id">ID : {activity.id}</span>
                      </div>
                      <div className="activity-amount" style={{
                        color: activity.type === 'win' ? '#00ff88' : '#ff4444'
                      }}>
                        {activity.amount}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Adminonly>
    </Protected>
  );
}