import React, { useState, useRef, useEffect } from "react";
import useTheme from "../hook/useTheme";

export default function ThemeSwitcher() {
  const [theme, setTheme] = useTheme();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleChange = (value) => {
    setTheme(value);
    setOpen(false);
  };

  const getIcon = () => (theme === "dark" ? "🌙" : "☀");

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="btn btn-circle btn-sm bg-base-200 hover:bg-base-300 shadow"
        title="Switch theme"
      >
        <span className="text-lg">{getIcon()}</span>
      </button>

      {open && (
        <ul className="absolute right-0 mt-2 z-50 menu p-2 shadow bg-base-100 rounded-box w-32">
          <li>
            <button onClick={() => handleChange("light")}>☀ Light</button>
          </li>
          <li>
            <button onClick={() => handleChange("dark")}>🌙 Dark</button>
          </li>
        </ul>
      )}
    </div>
  );
}
