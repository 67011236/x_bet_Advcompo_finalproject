"use client";
import { useState } from "react";
import AuthenticatedHeader from "../../components/AuthenticatedHeader";
import Protected from "../../components/Protected";

export default function ReportPage() {
  const [reportData, setReportData] = useState({
    title: "",
    description: "",
    category: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Implement report submission
    console.log("Report submitted:", reportData);
    alert("Report submitted successfully");
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
        
        <div className="container">
          <div className="report-form">
            <h1>Submit Report</h1>
            
            <form onSubmit={handleSubmit}>
              <div className="field">
                <label>Report Title</label>
                <input
                  type="text"
                  name="title"
                  value={reportData.title}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="field">
                <label>Category</label>
                <select
                  name="category"
                  value={reportData.category}
                  onChange={handleChange}
                  required
                >
                  <option value="">Select Category</option>
                  <option value="technical">Technical Issue</option>
                  <option value="payment">Payment Issue</option>
                  <option value="account">Account Issue</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="field">
                <label>Description</label>
                <textarea
                  name="description"
                  value={reportData.description}
                  onChange={handleChange}
                  rows="5"
                  required
                />
              </div>

              <button type="submit" className="btn">
                Submit Report
              </button>
            </form>
          </div>
        </div>
      </div>
    </Protected>
  );
}