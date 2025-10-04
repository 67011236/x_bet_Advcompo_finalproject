"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    const logout = async () => {
      try {
        // เรียก logout endpoint เพื่อ clear cookies
        await fetch("http://localhost:8000/logout", {
          method: "POST",
          credentials: "include",
        });
      } catch (error) {
        console.error("Logout error:", error);
      } finally {
        // redirect กลับไปหน้า login เสมอ
        router.push("/login");
      }
    };

    logout();
  }, [router]);

  return (
    <div style={{ 
      display: "flex", 
      justifyContent: "center", 
      alignItems: "center", 
      height: "100vh",
      backgroundColor: "#0d1421",
      color: "white"
    }}>
      <div style={{ textAlign: "center" }}>
        <h1>Logging out...</h1>
        <p>Please wait while we log you out</p>
      </div>
    </div>
  );
}