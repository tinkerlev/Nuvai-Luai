// file: AuthContext.jsx
import React, { createContext, useState, useEffect, useContext } from "react";

export const AuthContext = createContext(null);
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [authError, setAuthError] = useState(null);
  const fetchAuthStatus = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/auth/userinfo`, {
        credentials: "include",
      });   
      if (response.ok) {
        const data = await response.json();
        if (data && data.user) {
          setUser(data.user);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (err) {
      setUser(null);
    } finally {
      setCheckingAuth(false);
    }
  };
  useEffect(() => {
    fetchAuthStatus();
  }, []); 
  const logout = async () => {
    try {
      await fetch(`${process.env.REACT_APP_API_URL}/auth/logout`, {
        method: "POST",
        credentials: "include",
      });
      setUser(null);
      setAuthError(null);
    } catch (error) {
    }
  };
  const value = {
      user,
      setUser,
      checkingAuth,
      authError,
      refetchAuth: fetchAuthStatus,
      logout
  };
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};