"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import "../styles/header.css";

export default function AuthenticatedHeader() {
  const [userEmail, setUserEmail] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await fetch("http://localhost:8000/me", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        const userData = await response.json();
        setUserEmail(userData.email);
        setIsAdmin(userData.is_admin || false);
      }
    } catch (error) {
      console.error("Failed to fetch user data:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <header className="navbar">
      {/* โลโก้ฝั่งซ้าย */}
      <div className="logo">
        <span className="one">1</span>
        <span className="red">x</span>
        <span className="bet">BET</span>
      </div>

      {/* เมนูฝั่งขวา */}
      <nav className="menu">
        <Link href="/game_selection">GAME SELECTION</Link>
        <Link href="/balance">BALANCE</Link>
        <Link href="/report">REPORTS</Link>
        
        {/* Admin menus - แสดงเฉพาะ admin */}
        {!loading && isAdmin && (
          <>
            <Link href="/view-reports(admin)">VIEW REPORTS</Link>
            <Link href="/dashboard(admin)">DASHBOARD</Link>
          </>
        )}

        {!loading && userEmail && (
          <span className="user-email">{userEmail}</span>
        )}

        <Link href="/logout" className="logout">
          Logout
        </Link>
      </nav>
    </header>
  );
}