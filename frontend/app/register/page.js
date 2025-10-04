"use client";
import { useState } from "react";
import Link from "next/link";
import LoginHeader from "../../components/LoginHeader";
import "../../styles/register.css";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: "",
    age: "",
    phone: "",
    email: "",
    password: "",
    confirm_password: "",
    agree: false,
  });
  const [showPassword, setShowPassword] = useState({
    password: false,
    confirm_password: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });

    // Real-time validation
    validateField(name, type === "checkbox" ? checked : value);
  };

  const validateField = (name, value) => {
    const errors = { ...validationErrors };

    switch (name) {
      case "email":
        if (value && !value.endsWith("@gmail.com")) {
          errors.email = "Email must end with @gmail.com";
        } else {
          delete errors.email;
        }
        break;
      case "phone":
        if (value && !/^0\d{9}$/.test(value)) {
          errors.phone = "Phone must start with 0 and contain 10 digits";
        } else {
          delete errors.phone;
        }
        break;
      case "age":
        if (value && parseInt(value) < 20) {
          errors.age = "Age must be at least 20";
        } else {
          delete errors.age;
        }
        break;
      case "confirm_password":
        if (value && value !== formData.password) {
          errors.confirm_password = "Passwords do not match";
        } else {
          delete errors.confirm_password;
        }
        break;
      case "password":
        if (formData.confirm_password && formData.confirm_password !== value) {
          errors.confirm_password = "Passwords do not match";
        } else {
          delete errors.confirm_password;
        }
        break;
    }

    setValidationErrors(errors);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    // Check if passwords match
    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      setLoading(false);
      return;
    }

    // Check if user agreed to terms
    if (!formData.agree) {
      setError("You must agree to Terms & Privacy");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to login page
        window.location.href = "/login";
      } else {
        setError(data.error || "Registration failed");
      }
    } catch (err) {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const togglePassword = (field) => {
    setShowPassword({
      ...showPassword,
      [field]: !showPassword[field],
    });
  };

  return (
    <div className="page">
      {/* Header */}
      <LoginHeader />

      {/* Main Content */}
      <main className="container">
        <div className="grid">
          {/* LEFT: REGISTER FORM */}
          <section className="panel">
            <h1>Sign up</h1>

            <form className="register-form" onSubmit={handleSubmit}>
              {error && (
                <div className="error-box">
                  <p>{error}</p>
                </div>
              )}

              {/* Full name */}
              <div className="field">
                <label>Full name</label>
                <input
                  className="input"
                  type="text"
                  name="full_name"
                  placeholder="Your full name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                />
              </div>

              {/* Age */}
              <div className="field">
                <label>Age</label>
                <input
                  className="input"
                  type="number"
                  name="age"
                  placeholder="e.g. 20"
                  min="20"
                  step="1"
                  value={formData.age}
                  onChange={handleChange}
                  required
                />
                {validationErrors.age && (
                  <p className="form-error">{validationErrors.age}</p>
                )}
              </div>

              {/* Phone */}
              <div className="field">
                <label>Phone number</label>
                <input
                  className="input"
                  type="tel"
                  name="phone"
                  placeholder="0xxxxxxxxx"
                  pattern="^0\d{9}$"
                  minLength="10"
                  maxLength="10"
                  value={formData.phone}
                  onChange={handleChange}
                  required
                />
                {validationErrors.phone && (
                  <p className="form-error">{validationErrors.phone}</p>
                )}
              </div>

              {/* Email */}
              <div className="field">
                <label>Email Address</label>
                <input
                  className="input"
                  type="email"
                  name="email"
                  placeholder="yourname@gmail.com"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
                {validationErrors.email && (
                  <p className="form-error">{validationErrors.email}</p>
                )}
              </div>

              <div className="row">
                <div className="field col">
                  <label>Password</label>
                  <div className="password-wrap">
                    <input
                      className="input"
                      type={showPassword.password ? "text" : "password"}
                      name="password"
                      placeholder="Enter password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                    />
                    <button
                      type="button"
                      className="eye"
                      onClick={() => togglePassword("password")}
                      aria-label="Toggle password"
                    >
                      {showPassword.password ? "🙈" : "👁️"}
                    </button>
                  </div>
                </div>

                <div className="field col">
                  <label>Confirm Password</label>
                  <div className="password-wrap">
                    <input
                      className="input"
                      type={showPassword.confirm_password ? "text" : "password"}
                      name="confirm_password"
                      placeholder="Confirm password"
                      value={formData.confirm_password}
                      onChange={handleChange}
                      required
                    />
                    <button
                      type="button"
                      className="eye"
                      onClick={() => togglePassword("confirm_password")}
                      aria-label="Toggle confirm password"
                    >
                      {showPassword.confirm_password ? "🙈" : "👁️"}
                    </button>
                  </div>
                  {validationErrors.confirm_password && (
                    <p className="form-error">{validationErrors.confirm_password}</p>
                  )}
                </div>
              </div>

              {/* Agree to terms */}
              <p className="subtle">
                <label className="checkbox-wrapper">
                  <input
                    type="checkbox"
                    name="agree"
                    checked={formData.agree}
                    onChange={handleChange}
                    required
                  />
                  <span>
                    I agree to the <a href="#">Terms of Service</a> and{" "}
                    <a href="#">Privacy Policy</a>.
                  </span>
                </label>
              </p>

              {/* Submit */}
              <button className="btn" type="submit" disabled={loading}>
                {loading ? "Signing up..." : "Sign up"}
              </button>

              <p className="subtle" style={{ textAlign: "left", marginTop: "12px" }}>
                Already have an account?{" "}
                <Link href="/login" style={{ color: "#2f6dff" }}>
                  Log in
                </Link>
              </p>
            </form>
          </section>

          {/* RIGHT: HERO TEXT */}
          <section className="hero-block">
            <h2 className="hero-title">JOIN FOR FREE</h2>
            <p className="hero-desc">
              Investment comes with risks, but they are risks that create opportunities and value.
              <br />
              <span className="red">High Risk, High Returns</span> — start your journey with us today
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
