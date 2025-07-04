// AuthContext.jsx
import React, { createContext, useState, useContext, useEffect, useCallback } from "react";
export const AuthContext = createContext(undefined);
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState(null);

const fetchAuthStatus = useCallback(async () => {
    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/userinfo`, {
        method: "GET",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        }
      });

      if (!res.ok) throw new Error("Unauthorized");

      const { user } = await res.json();
      setUser(user || null);

    } catch (err) {
      if (process.env.NODE_ENV === "development") {
        console.error("Auth error:", err.message);
      }
      setUser(null);
      setAuthError("Auth error");

    } finally {
      setCheckingAuth(false);
    }
  }, []);
  useEffect(() => {
    fetchAuthStatus();
  }, [fetchAuthStatus]);
  
  const logout = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        }
      });
    } catch (e) {
      console.warn("Logout failed silently.");
    } finally {
      setUser(null);
      setAuthError(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        checkingAuth,
        authError,
        refetchAuth: fetchAuthStatus,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an <AuthProvider>");
  }
  return context;
};
