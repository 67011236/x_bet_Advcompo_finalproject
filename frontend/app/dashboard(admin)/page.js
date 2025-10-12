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
    { name: "Premium Wheel", percentage: 50, color: "#71ddff", total_plays: 0 },
    { name: "Rock-Paper-Scissors", percentage: 50, color: "#4a9eff", total_plays: 0 }
  ]);

  const [realtimeActivities, setRealtimeActivities] = useState([]);
  
  const [reportTypesData, setReportTypesData] = useState([
    { type: "Technical Issue", value: 0, color: "#71ddff" },
    { type: "Payment Issue", value: 0, color: "#71ddff" },
    { type: "Account Issue", value: 0, color: "#71ddff" },
    { type: "Betting Issue", value: 0, color: "#71ddff" },
    { type: "Suggestion", value: 0, color: "#71ddff" },
    { type: "Other", value: 0, color: "#71ddff" }
  ]);

  const fetchReportTypes = async () => {
    try {
      console.log("🔄 Fetching report categories from database...");
      const response = await fetch("http://localhost:8000/api/report-categories", {
        credentials: 'include'
      });
      
      console.log("📊 Report categories response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("✅ Report categories data received:", data);
        setReportTypesData(data.categories);
        console.log("📈 Report categories updated:", data.categories);
      } else {
        const errorText = await response.text();
        console.error("❌ Failed to fetch report categories:", response.status, errorText);
      }
    } catch (error) {
      console.error("💥 Error fetching report categories:", error);
    }
  };

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

  const fetchGameStats = async () => {
    try {
      console.log("🔄 Fetching game stats...");
      const response = await fetch("http://localhost:8000/api/game-stats", {
        credentials: 'include'
      });
      
      console.log("📊 Game stats response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("✅ Game stats data received:", data);
        setGameStats(data.game_stats);
        setRealtimeActivities(data.recent_activities);
        console.log("📈 Pie chart data updated:", data.game_stats);
      } else {
        const errorText = await response.text();
        console.error("❌ Failed to fetch game stats:", response.status, errorText);
        
        // Fallback: ถ้าไม่สามารถเรียก game-stats ได้ ให้เรียกข้อมูลจากตาราง game โดยตรง
        try {
          console.log("🔄 Trying fallback method to fetch game counts...");
          
          // เรียก API เพื่อดึงจำนวน Game1
          const game1Response = await fetch("http://localhost:8000/api/game1/count", {
            credentials: 'include'
          });
          
          // เรียก API เพื่อดึงจำนวน Game2  
          const game2Response = await fetch("http://localhost:8000/api/game2/count", {
            credentials: 'include'
          });
          
          if (game1Response.ok && game2Response.ok) {
            const game1Data = await game1Response.json();
            const game2Data = await game2Response.json();
            
            const game1Total = game1Data.count || 0;
            const game2Total = game2Data.count || 0;
            const totalPlays = game1Total + game2Total;
            
            let game1Percentage = 50.0;
            let game2Percentage = 50.0;
            
            if (totalPlays > 0) {
              game1Percentage = Math.round((game1Total / totalPlays) * 100 * 10) / 10;
              game2Percentage = Math.round((game2Total / totalPlays) * 100 * 10) / 10;
            }
            
            const fallbackGameStats = [
              {
                name: "Premium Wheel",
                percentage: game1Percentage,
                color: "#71ddff",
                total_plays: game1Total
              },
              {
                name: "Rock-Paper-Scissors", 
                percentage: game2Percentage,
                color: "#4a9eff",
                total_plays: game2Total
              }
            ];
            
            setGameStats(fallbackGameStats);
            console.log("✅ Fallback game stats updated:", fallbackGameStats);
          }
          
        } catch (fallbackError) {
          console.error("💥 Fallback method also failed:", fallbackError);
        }
      }
    } catch (error) {
      console.error("💥 Error fetching game stats:", error);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
    fetchGameStats();
    fetchReportTypes(); // ดึงข้อมูล report categories เริ่มต้น
    
    // Set up interval to refresh stats every 5 seconds for real-time updates
    const statsInterval = setInterval(fetchDashboardStats, 10000);
    const gameStatsInterval = setInterval(fetchGameStats, 5000); // More frequent for real-time feel
    const reportCategoriesInterval = setInterval(fetchReportTypes, 5000); // อัปเดต report categories ทุก 5 วินาที
    
    return () => {
      clearInterval(statsInterval);
      clearInterval(gameStatsInterval);
      clearInterval(reportCategoriesInterval);
    };
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
                        stroke={gameStats[0]?.color || "#71ddff"}
                        strokeWidth="15"
                        strokeDasharray={`${(gameStats[0]?.percentage || 50) * 2.51} 251`}
                        strokeDashoffset="0"
                        transform="rotate(-90 60 60)"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="40"
                        fill="none"
                        stroke={gameStats[1]?.color || "#4a9eff"}
                        strokeWidth="15"
                        strokeDasharray={`${(gameStats[1]?.percentage || 50) * 2.51} 251`}
                        strokeDashoffset={`-${(gameStats[0]?.percentage || 50) * 2.51}`}
                        transform="rotate(-90 60 60)"
                      />
                    </svg>
                    <div className="chart-center-text">
                      <div className="total-plays">
                        {(gameStats[0]?.total_plays || 0) + (gameStats[1]?.total_plays || 0)}
                      </div>
                      <div className="plays-label">Plays</div>
                    </div>
                  </div>
                  <div className="chart-legend">
                    {gameStats.map((game, index) => (
                      <div key={index} className="legend-item">
                        <span className="legend-color" style={{backgroundColor: game.color}}></span>
                        <span className="legend-text">
                          {game.name} ({game.total_plays || 0})
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Bottom Grid */}
            <div className="bottom-grid">
              {/* Report Types Chart */}
              <div className="chart-card-large">
                <h3>Report Categories</h3>
                <div className="bar-chart">
                  {(() => {
                    const dataWithValues = reportTypesData.filter(item => item.value > 0);
                    const maxValue = dataWithValues.length > 0 ? Math.max(...dataWithValues.map(d => d.value)) : 1;
                    
                    return dataWithValues.map((item, index) => (
                      <div key={index} className="bar-container">
                        <div 
                          className="bar" 
                          style={{
                            height: `${(item.value / maxValue) * 85}%` // ใช้ 85% เป็นความสูงสูงสุด
                          }}
                        ></div>
                        <div className="bar-labels">
                          <span className="bar-label">{item.type.split(' ')[0]}</span>
                          <span className="bar-count">{item.value}</span>
                        </div>
                      </div>
                    ));
                  })()}
                </div>
                {reportTypesData.filter(item => item.value > 0).length === 0 && (
                  <div className="no-data-message">
                    <p>No reports available yet</p>
                  </div>
                )}
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