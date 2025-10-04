"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import LoginHeader from "../../components/LoginHeader";
import "../../styles/login.css";

export default function LoginPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    console.log("Submitting login with data:", formData);

    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      console.log("Response status:", response.status);
      console.log("Response ok:", response.ok);

      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
        console.log("Login successful, redirecting to /balance");
        // Add a small delay before redirect
        setTimeout(() => {
          try {
            router.push("/balance");
          } catch (routerError) {
            console.log("Router failed, using window.location");
            window.location.replace("/balance");
          }
        }, 100);
      } else {
        console.log("Login failed with error:", data.error);
        setError(data.error || "Login failed");
      }
    } catch (err) {
      console.error("Network error:", err);
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const togglePassword = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="page">
      {/* Header */}
      <LoginHeader />

      {/* Main Content */}
      <main className="container">
        {/* LOGIN CARD */}
        <section className="login-box">
          <h2>Log in</h2>

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                name="email"
                placeholder="Enter email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="field">
              <label>Password</label>
              <div className="input-with-eye">
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="Enter password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
                <button
                  type="button"
                  className="eye-btn"
                  onClick={togglePassword}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? "🙈" : "👁️"}
                </button>
              </div>
            </div>

            {error && <p className="form-error">{error}</p>}

            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Logging in..." : "Log in"}
            </button>
          </form>

          <p className="meta">
            Don't have an account?{" "}
            <Link href="/register" className="link">
              Sign up
            </Link>
          </p>
        </section>

        {/* WELCOME TEXT */}
        <section className="welcome">
          <h1>WELCOME BACK</h1>
          <p>Your first step to investing start here - log in</p>
        </section>
      </main>
    </div>
  );
}