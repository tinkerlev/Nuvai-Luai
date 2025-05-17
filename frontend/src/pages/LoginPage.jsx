import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [lockoutUntil, setLockoutUntil] = useState(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [passwordScore, setPasswordScore] = useState(null);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem("lockoutUntil");
    if (saved) {
      const until = new Date(saved);
      if (until > new Date()) {
        setLockoutUntil(until);
      } else {
        localStorage.removeItem("lockoutUntil");
        localStorage.removeItem("failCount");
      }
    }
  }, []);

  useEffect(() => {
    if (!lockoutUntil) return;
    const interval = setInterval(() => {
      const now = new Date();
      const diff = Math.max(0, lockoutUntil - now);
      setTimeLeft(Math.floor(diff / 1000));
      if (diff <= 0) {
        clearInterval(interval);
        setLockoutUntil(null);
        setTimeLeft(0);
        localStorage.removeItem("lockoutUntil");
        localStorage.removeItem("failCount");
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [lockoutUntil]);

  const validateEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const validatePassword = (pwd) => {
    return (
      pwd.length >= 12 &&
      /[A-Z]/.test(pwd) &&
      /[a-z]/.test(pwd) &&
      /[0-9]/.test(pwd) &&
      /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(pwd) &&
      !/\s/.test(pwd)
    );
  };

  const sanitizeInput = (input) => input.replace(/[<>"']/g, "").normalize("NFKC");

  const formatTimeLeft = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePasswordChange = (value) => {
    setPassword(value);
    let score = 0;
    if (value.length >= 12) score++;
    if (/[A-Z]/.test(value)) score++;
    if (/[a-z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(value)) score++;
    setPasswordScore(score);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!termsAccepted) {
      setErrorMsg("Please accept the terms and conditions");
      return;
    }
    if (loading) return;

    if (lockoutUntil && new Date() < lockoutUntil) {
      setErrorMsg("Too many failed attempts. Try again later.");
      return;
    }

    const cleanEmail = sanitizeInput(email.trim());
    const cleanPassword = sanitizeInput(password);

    if (!validateEmail(cleanEmail)) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }

    if (!validatePassword(cleanPassword)) {
      setErrorMsg("Invalid email or password.");
      return;
    }

    setLoading(true);
    setErrorMsg("");

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 8000);
      const csrfToken = localStorage.getItem("csrfToken") || "";
      const nonce = crypto.randomUUID();

      const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Client-Nonce": nonce,
          "X-CSRF-Token": csrfToken,
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ email: cleanEmail, password: cleanPassword }),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!res.ok) {
        const errData = await res.json();
        setErrorMsg(errData.message || "Invalid email or password.");

        const attempts = parseInt(localStorage.getItem("failCount") || "0", 10) + 1;
        if (attempts >= 3) {
          const until = new Date(Date.now() + 5 * 60 * 1000);
          localStorage.setItem("lockoutUntil", until);
          setLockoutUntil(until);
        } else {
          localStorage.setItem("failCount", attempts);
        }

        setLoading(false);
        return;
      }

      const data = await res.json();
      if (data.token && data.csrfToken) {
        localStorage.setItem("authToken", data.token);
        localStorage.setItem("csrfToken", data.csrfToken);
        localStorage.removeItem("failCount");
        localStorage.removeItem("lockoutUntil");
        navigate("/scan");
      } else {
        setErrorMsg("Invalid server response. Please try again.");
      }
    } catch (err) {
      if (err.name === "AbortError") {
        setErrorMsg("Login request timed out. Please try again.");
      } else {
        console.error("Login error:", err);
        setErrorMsg("Unexpected error occurred. Please try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  };

  return (
    <div className="min-h-screen bg-base-200 flex items-center justify-center p-4">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeIn}
        className="w-full max-w-md"
      >
        <div className="card w-full bg-base-100 shadow-xl border border-base-300">
          <div className="card-body">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon icon="mdi:lock" className="w-8 h-8 text-primary"/>
              </div>
            </div>
            
            <h2 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Secure Login
            </h2>
            
            <form onSubmit={handleSubmit}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Email</span>
                </label>
                <input
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input input-bordered w-full"
                  required
                  autoComplete="username"
                />
              </div>
              
              <div className="form-control mb-2">
                <label className="label">
                  <span className="label-text">Password</span>
                </label>
                <input
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => handlePasswordChange(e.target.value)}
                  className="input input-bordered w-full"
                  required
                  autoComplete="current-password"
                  onPaste={(e) => e.preventDefault()}
                />
              </div>
              
              {passwordScore !== null && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mb-4"
                >
                  <progress 
                    className={`progress w-full ${
                      passwordScore >= 5 ? "progress-success" : 
                      passwordScore >= 3 ? "progress-warning" : "progress-error"
                    }`} 
                    value={passwordScore} 
                    max="5"
                  ></progress>
                  <p className="text-xs mt-1 text-center">
                    Password strength: {passwordScore}/5
                  </p>
                </motion.div>
              )}
              
              {errorMsg && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="alert alert-error mb-4"
                >
                  <Icon icon="mdi:alert-circle" className="h-6 w-6" />
                  <span>{errorMsg}</span>
                </motion.div>
              )}
              
              {timeLeft > 0 && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="alert alert-warning mb-4"
                >
                  <Icon icon="mdi:clock-outline" className="h-6 w-6" />
                  <span>Locked out. Please wait {formatTimeLeft(timeLeft)} before trying again.</span>
                </motion.div>
              )}
              
              <div className="form-control mb-4">
                <label className="label cursor-pointer justify-start gap-2">
                  <input 
                    type="checkbox" 
                    className="checkbox checkbox-sm checkbox-primary" 
                    checked={termsAccepted}
                    onChange={() => setTermsAccepted(!termsAccepted)}
                  />
                  <span className="label-text">I accept the Terms and Conditions</span>
                </label>
              </div>
              
              <button
                type="submit"
                disabled={loading || timeLeft > 0 || !termsAccepted}
                className={`btn btn-primary w-full ${loading ? "loading" : ""}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Logging in
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Icon icon="mdi:login" className="mr-2" />
                    Login
                  </span>
                )}
              </button>
            </form>
            
            <div className="divider my-4">OR</div>
            
            <div className="text-sm text-center space-y-2">
              <Link to="/register" className="link link-primary block hover:underline">
                Create a new account
              </Link>
              <Link to="/forgot-password" className="link link-secondary block hover:underline">
                Forgot your password?
              </Link>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
