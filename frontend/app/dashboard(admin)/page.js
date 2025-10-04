"use client";
import { useState, useEffect } from "react";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import Protected from "../../components/Protected";
import Adminonly from "../../components/Adminonly";
import "../../styles/admin.css";

export default function AdminDashboard() {
  const [stats, setStats] = useState({
    totalUsers: 0,
    totalReports: 0,
    totalBalance: 0,
  });

  useEffect(() => {
    // TODO: Fetch admin stats from API
    setStats({
      totalUsers: 150,
      totalReports: 25,
      totalBalance: 500000,
    });
  }, []);

  return (
    <Protected>
      <Adminonly>
        <div className="admin-dashboard">
          <AuthenticatedHeader />
          
          <div className="container">
            <div className="dashboard-header">
              <h1>Admin Dashboard</h1>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Total Users</h3>
                <div className="stat-number">{stats.totalUsers}</div>
              </div>
              
              <div className="stat-card">
                <h3>Total Reports</h3>
                <div className="stat-number">{stats.totalReports}</div>
              </div>
              
              <div className="stat-card">
                <h3>Total Balance</h3>
                <div className="stat-number">{stats.totalBalance.toLocaleString()} THB</div>
              </div>
            </div>

            <div className="admin-actions">
              <h2>Admin Actions</h2>
              <div className="action-buttons">
                <button className="btn">Manage Users</button>
                <button className="btn">View Reports</button>
                <button className="btn">Financial Reports</button>
                <button className="btn">System Settings</button>
              </div>
            </div>
          </div>
        </div>
      </Adminonly>
    </Protected>
  );
}