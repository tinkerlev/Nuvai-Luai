import { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTheme } from "../hook/useTheme";
import { jwtDecode } from "jwt-decode";
import { AuthContext } from "../contexts/AuthContext";

// Utility to safely decode JWT and check expiration
const isTokenValid = (token) => {
  try {
    const { exp } = jwtDecode(token);
    return exp * 1000 > Date.now(); // Convert to milliseconds
  } catch (err) {
    console.warn("⚠️ Invalid JWT structure");
    return false;
  }
};

export default function useAuth(requireAuth = false) {
  const { user, setUser, checkingAuth } = useContext(AuthContext);
  const [authError, setAuthError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { theme } = useTheme();

  // Fetch user and validate token (silent check)
  const verifyAuth = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/userinfo`, {
        method: "GET",
        credentials: "include",
        headers: { "Content-Type": "application/json" }
      });

      if (!res.ok) throw new Error("❌ Authentication failed");

      const data = await res.json();

      const token = getCookie("luai.jwt");
      if (!token || !isTokenValid(token)) {
        throw new Error("❌ Token expired or invalid");
      }

      setUser(data.user);
      setAuthError(null);
    } catch (err) {
      console.warn("🔒 Auth error:", err.message);
      setUser(null);
      setAuthError("Session expired or unauthorized.");
      if (requireAuth) navigate("/login");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    verifyAuth();
  }, []);

  // Helper: get cookie securely
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
  };

  return {
    user,
    isAuthenticated: !!user,
    checkingAuth,
    authError,
    loading,
    theme
  };
}