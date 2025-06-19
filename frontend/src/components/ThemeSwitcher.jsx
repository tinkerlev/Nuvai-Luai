// ThemeSwitcher.jsx
import React from "react";
import useTheme from "../hook/useTheme";

export default function ThemeSwitcher({ onSelect }) {
  const [theme, setTheme] = useTheme();

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    onSelect?.();
  };

  return (
    <button
      onClick={toggleTheme}
      className="w-full justify-start flex items-center gap-2 px-4 py-2"
    >
      {theme === "light" ? "🌙 Switch to Dark" : "☀ Switch to Light"}
    </button>
  );
}
