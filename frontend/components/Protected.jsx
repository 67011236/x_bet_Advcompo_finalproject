"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Protected({ children }) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const response = await fetch("http://localhost:8000/me", {
        method: "GET",
        credentials: "include",
      });

      if (response.ok) {
        setIsAuthenticated(true);
      } else {
        // Not authenticated, redirect to login
        router.push("/login");
        return;
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      // Network error, also redirect to login
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
        <div>Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect anyway
  }

  return children;
}