"use client";
import "../styles/header.css";

export default function LoginHeader() {
  return (
    <header className="navbar">
      {/* โลโก้ฝั่งซ้าย */}
      <div className="logo">
        <span className="one">1</span>
        <span className="red">x</span>
        <span className="bet">BET</span>
      </div>
    </header>
  );
}