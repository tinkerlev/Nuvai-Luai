// LoginOptions.jsx
import React from "react";
import { ALLOWED_PROVIDERS, PROVIDER_ICONS } from "../constants/providers";
import { useLocation } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:5000";
const providers = [
  {
    name: "Google",
    id: "google",
    icon: PROVIDER_ICONS.google
  },
  {
    name: "GitHub",
    id: "github",
    icon: PROVIDER_ICONS.github
  },
  {
    name: "LinkedIn",
    id: "linkedin",
    icon: PROVIDER_ICONS.linkedin
  },
];

export default function LoginOptions({ setFailedCount, setLockoutTimeLeft }) {
  const location = useLocation();
  const currentPath = location.pathname || "/login";
  const handleLogin = (provider) => {
    try {
      if (!ALLOWED_PROVIDERS.includes(provider)) {
        console.warn(`Provider "${provider}" is not allowed.`);
        return;
      }
  const encodedReturnTo = encodeURIComponent(currentPath);
  window.location.replace(`${API_BASE}/auth/login/${provider}?returnTo=${encodedReturnTo}`);
    } catch (err) {
      console.error("Login failed:", err);
      if (typeof setFailedCount === "function") {
        setFailedCount((prev) => (prev || 0) + 1);
      }
      if (typeof setLockoutTimeLeft === "function") {
        setLockoutTimeLeft(60);
      }
    }
  };

  return (
    <div className="flex justify-center gap-4">
      {providers.map(({ name, id, icon }) => (
        <button
          key={id}
          onClick={() => handleLogin(id)}
          className="w-10 h-10 flex items-center justify-center rounded-full border hover:shadow transition bg-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
          title={`Sign in with ${name}`}
          aria-label={`Sign in with ${name}`}
        >
          <img
            src={icon}
            alt={`${name} logo`}
            className="w-5 h-5"
            crossOrigin="anonymous"
            referrerPolicy="no-referrer"
            loading="lazy"
            draggable="false"
          />
        </button>
      ))}
    </div>
  );
}
