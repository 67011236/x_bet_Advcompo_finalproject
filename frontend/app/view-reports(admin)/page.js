"use client";
import { useState, useEffect } from "react";
import Protected from "../../components/Protected";
import Adminonly from "../../components/Adminonly";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "../../styles/admin.css";

export default function ViewReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await fetch("http://localhost:8000/reports", {
        credentials: "include",
      });
      
      if (response.ok) {
        const data = await response.json();
        setReports(data.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch reports:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Protected>
      <Adminonly>
        <div className="view-reports">
          <AuthenticatedHeader />
          
          <div className="container">
            <div className="reports-header">
              <h1>User Reports</h1>
              <p>Manage and review all user-submitted reports</p>
            </div>
            
            {loading ? (
              <div className="loading">Loading reports...</div>
            ) : (
              <div className="reports-grid">
                {reports.length === 0 ? (
                  <div className="no-reports">
                    <p>No reports found</p>
                  </div>
                ) : (
                  reports.map((report) => (
                    <div key={report.id} className="report-card">
                      <h3>{report.name}</h3>
                      <div className="report-actions">
                        <button className="btn btn-primary">View Details</button>
                        <button className="btn btn-secondary">Mark Resolved</button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </Adminonly>
    </Protected>
  );
}