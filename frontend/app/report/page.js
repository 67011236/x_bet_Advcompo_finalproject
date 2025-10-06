"use client";
import { useState, useEffect } from "react";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import Protected from "../../components/Protected";
import "../../styles/report.css";

export default function ReportPage() {
  const [reportData, setReportData] = useState({
    title: "",
    description: "",
    category: "",
  });
  
  const [userEmail, setUserEmail] = useState("");

  useEffect(() => {
    // ดึง user email จาก API /me
    const fetchUserData = async () => {
      try {
        const response = await fetch("http://localhost:8000/me", {
          credentials: 'include'
        });
        if (response.ok) {
          const userData = await response.json();
          setUserEmail(userData.email);
        }
      } catch (error) {
        console.error("Error fetching user data:", error);
      }
    };
    
    fetchUserData();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // ตรวจสอบข้อมูล
    if (!reportData.title || !reportData.category || !reportData.description) {
      alert("Please fill in all fields");
      return;
    }
    
    try {
      console.log("Submitting report:", reportData);
      
      const response = await fetch("http://localhost:8000/api/submit-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(reportData),
      });
      
      const data = await response.json();
      console.log("Response:", data);
      
      if (response.ok) {
        // Show success message
        const successMessage = document.createElement('div');
        successMessage.className = 'success-toast';
        successMessage.textContent = `Report submitted successfully! (ID: ${data.report_id})`;
        document.body.appendChild(successMessage);
        
        setTimeout(() => {
          if (document.body.contains(successMessage)) {
            document.body.removeChild(successMessage);
          }
        }, 4000);
        
        // Reset form
        setReportData({
          title: "",
          description: "",
          category: "",
        });
        
        console.log("✅ Report submitted successfully!");
      } else {
        throw new Error(data.detail || "Failed to submit report");
      }
      
    } catch (error) {
      console.error("Error submitting report:", error);
      
      // Show error message
      const errorMessage = document.createElement('div');
      errorMessage.className = 'error-toast';
      errorMessage.textContent = `Error: ${error.message}`;
      document.body.appendChild(errorMessage);
      
      setTimeout(() => {
        if (document.body.contains(errorMessage)) {
          document.body.removeChild(errorMessage);
        }
      }, 4000);
    }
  };

  const handleChange = (e) => {
    setReportData({
      ...reportData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Protected>
      <div className="report-page">
        <AuthenticatedHeader />
        
        <div className="report-container">
          {/* Background Effects */}
          <div className="bg-effects">
            <div className="light-effect light-1"></div>
            <div className="light-effect light-2"></div>
            <div className="light-effect light-3"></div>
          </div>
          
          {/* Header */}
          <div className="report-header">
            <h1>Report Issue and Suggestions</h1>
          </div>
          
          {/* Report Form Card */}
          <div className="report-card">
            <div className="card-header">
              <h2>Write Report here</h2>
            </div>
            
            <form onSubmit={handleSubmit} className="report-form">
              <div className="form-group">
                <input
                  type="text"
                  name="title"
                  placeholder="Report Title"
                  value={reportData.title}
                  onChange={handleChange}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <select
                  name="category"
                  value={reportData.category}
                  onChange={handleChange}
                  required
                  className="form-select"
                >
                  <option value="">Select Category</option>
                  <option value="technical">Technical Issue</option>
                  <option value="payment">Payment Issue</option>
                  <option value="account">Account Issue</option>
                  <option value="betting">Betting Issue</option>
                  <option value="suggestion">Suggestion</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="form-group">
                <textarea
                  name="description"
                  placeholder="Describe your issue or suggestion in detail..."
                  value={reportData.description}
                  onChange={handleChange}
                  rows="8"
                  required
                  className="form-textarea"
                />
              </div>

              <button 
                type="submit" 
                className="submit-btn"
                onMouseMove={(e) => {
                  const rect = e.currentTarget.getBoundingClientRect();
                  const x = ((e.clientX - rect.left) / rect.width) * 100;
                  const y = ((e.clientY - rect.top) / rect.height) * 100;
                  e.currentTarget.style.setProperty('--mouse-x', `${x}%`);
                  e.currentTarget.style.setProperty('--mouse-y', `${y}%`);
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.classList.add('wave-active');
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.classList.remove('wave-active');
                }}
              >
                submit
              </button>
            </form>
          </div>
        </div>
      </div>
    </Protected>
  );
}