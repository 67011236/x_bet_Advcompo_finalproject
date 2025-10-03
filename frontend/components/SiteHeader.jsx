"use client";
import Link from "next/link";
import "../styles/header.css";

export default function SiteHeader({ email }) {
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

        {email && <span className="user-email">{email}</span>}

        <Link href="/logout" className="logout">
          Logout
        </Link>
      </nav>
    </header>
  );
}
