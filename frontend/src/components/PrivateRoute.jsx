import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

export default function PrivateRoute({ children }) {
  const [isValid, setIsValid] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      setIsValid(false);
      return;
    }

    const validateToken = async () => {
      try {
        const [headerB64, payloadB64, signature] = token.split(".");
        if (!headerB64 || !payloadB64 || !signature) {
          setIsValid(false);
          return;
        }

        const header = JSON.parse(atob(headerB64));
        const payload = JSON.parse(atob(payloadB64));

        if (header.typ !== "JWT" || header.alg !== "HS256") {
          setIsValid(false);
          return;
        }

        const now = Math.floor(Date.now() / 1000);
        if (
          !payload.exp || now > payload.exp ||
          !payload.iat || payload.iat > now ||
          !payload.sub || typeof payload.sub !== "string" ||
          !payload.aud || payload.aud !== "nuvai-client" ||
          !payload.iss || payload.iss !== "nuvai-auth"
        ) {
          setIsValid(false);
          return;
        }

        const storedSession = localStorage.getItem("sessionID");
        if (payload.sid && storedSession && payload.sid !== storedSession) {
          setIsValid(false);
          return;
        }

        const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/userinfo`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        if (!res.ok) {
          setIsValid(false);
          return;
        }

        setIsValid(true);
      } catch (err) {
        console.error("Token validation error:", err);
        setIsValid(false);
      }
    };

    validateToken();
  }, []);

  if (isValid === null) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center text-gray-600 animate-pulse text-sm">
          🔒 Validating session...
        </div>
      </div>
    );
  }

  return isValid ? children : <Navigate to="/login" replace />;
}