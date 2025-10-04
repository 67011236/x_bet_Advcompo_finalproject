"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Adminonly({ children }) {
  const router = useRouter();
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAdminStatus();
  }, []);

  const checkAdminStatus = async () => {
    try {
      const response = await fetch("http://localhost:8000/me", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        const userData = await response.json();
        if (userData.is_admin) {
          setIsAdmin(true);
        } else {
          // Not admin, redirect to home page
          router.push("/");
          return;
        }
      } else {
        // Not authenticated, redirect to login
        router.push("/login");
        return;
      }
    } catch (error) {
      console.error("Admin check failed:", error);
      router.push("/login");
      return;
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div style={{ 
        display: "flex", 
        justifyContent: "center", 
        alignItems: "center", 
        height: "100vh" 
      }}>
        <div>Checking admin privileges...</div>
      </div>
    );
  }

  if (!isAdmin) {
    return null; // Will redirect anyway
  }

  return children;
}