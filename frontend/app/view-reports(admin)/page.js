"use client";
import { useState, useEffect } from "react";
import Protected from "../../components/Protected";
import Adminonly from "../../components/Adminonly";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import "../../styles/view-reports-admin.css";

export default function ViewReports() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const response = await fetch('http://localhost:8000/reports', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        console.log('API Response:', data); // Debug log
        
        // ตรวจสอบว่า data มี reports array หรือไม่
        if (data && Array.isArray(data.reports)) {
          setReports(data.reports);
        } else if (Array.isArray(data)) {
          setReports(data);
        } else {
          console.error('API response format invalid:', data);
          setReports([]); // ตั้งค่าเป็น array เปล่า
        }
      } else {
        console.error('Failed to fetch reports:', response.status);
        setReports([]); // ตั้งค่าเป็น array เปล่า
      }
    } catch (err) {
      console.error('Error fetching reports:', err);
      setReports([]); // ตั้งค่าเป็น array เปล่า
    } finally {
      setLoading(false);
    }
  };

  return (
    <Protected>
      <Adminonly>
        <div className="admin-container">
          <AuthenticatedHeader />
          <div className="admin-content">
            {/* Background Effects */}
            <div className="bg-effects">
              <div className="light-effect light-1"></div>
              <div className="light-effect light-2"></div>
              <div className="light-effect light-3"></div>
            </div>

            {/* Header */}
            <div className="report-header">
              <h1>User report Issue and Suggestions</h1>
            </div>
            
            {loading ? (
              <div className="loading">Loading...</div>
            ) : (
              <div className="reports-container">
                {Array.isArray(reports) && reports.length > 0 ? (
                  reports.map((report) => (
                    <div key={report.id} className="report-item">
                      <div className="user-email-badge">
                        ID : {report.user_email}
                      </div>
                      <div className="user-feedback-card">
                        <div className="feedback-content">
                          <div className="field-row">
                            <span className="field-label">Title:</span>
                            <span className="field-value">{report.title}</span>
                          </div>
                          <div className="field-row">
                            <span className="field-label">Category:</span>
                            <span className="field-value">{report.category}</span>
                          </div>
                          <div className="field-row">
                            <span className="field-label">Description:</span>
                            <span className="field-value">{report.description}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-reports">
                    <h3>No reports found</h3>
                    <p>There are no user reports at the moment.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Adminonly>
    </Protected>
  );
}