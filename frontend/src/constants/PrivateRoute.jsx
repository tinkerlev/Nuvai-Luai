import React, { useEffect } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../hook/useAuth";

export default function PrivateRoute({ children }) {
  const { user, checkingAuth } = useAuth();
  const location = useLocation();

  console.log("🛡️ PrivateRoute - checkingAuth:", checkingAuth);
  console.log("🛡️ PrivateRoute - user:", user);

  if (checkingAuth) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-lg font-medium animate-pulse">🔐 Checking authentication...</p>
      </div>
    );
  }

  if (!user) {
    console.warn("🚫 PrivateRoute - no user, redirecting to login");
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log("✅ PrivateRoute - user is authenticated, rendering protected route");
  return children;
}
