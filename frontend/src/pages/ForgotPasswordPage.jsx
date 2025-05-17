import React, { useState } from "react";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';
import { Link } from "react-router-dom";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const sanitizeInput = (input) => input.replace(/[<>"']/g, "").normalize("NFKC");
  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    setMessage("");

    const cleanEmail = sanitizeInput(email.trim());

    if (!validateEmail(cleanEmail)) {
      setErrorMsg("Please enter a valid email address.");
      return;
    }

    setLoading(true);

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      const csrfToken = localStorage.getItem("csrfToken") || "";

      const res = await fetch("https://localhost:5000/auth/forgot-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRF-Token": csrfToken,
        },
        body: JSON.stringify({ email: cleanEmail }),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!res.ok) {
        const errData = await res.json();
        setErrorMsg(errData.message || "Password reset request failed.");
        return;
      }

      setMessage("✅ If your email is valid, a reset link has been sent.");
    } catch (err) {
      if (err.name === "AbortError") {
        setErrorMsg("Request timed out. Please try again.");
      } else {
        console.error("Forgot password error:", err);
        setErrorMsg("Unexpected error occurred. Try again later.");
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
              <div className="w-16 h-16 rounded-full bg-info/10 flex items-center justify-center">
                <Icon icon="mdi:key" className="w-8 h-8 text-info"/>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Password Recovery
            </h2>
            
            <p className="text-center text-base-content/80 mb-6">
              Enter your email address and we'll send you a link to reset your password.
            </p>
            
            <form onSubmit={handleSubmit}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Email Address</span>
                </label>
                <input
                  type="email"
                  name="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input input-bordered w-full"
                  required
                  maxLength={100}
                  autoComplete="off"
                />
              </div>
              
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
              
              {message && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="alert alert-success mb-4"
                >
                  <Icon icon="mdi:check-circle" className="h-6 w-6" />
                  <span>{message}</span>
                </motion.div>
              )}
              
              <button
                type="submit"
                disabled={loading}
                className={`btn btn-primary w-full ${loading ? "loading" : ""}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Sending...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Icon icon="mdi:email-send" className="mr-2" />
                    Send Reset Link
                  </span>
                )}
              </button>
            </form>
            
            <div className="divider my-4"></div>
            
            <Link to="/login" className="btn btn-ghost btn-sm">
              <Icon icon="mdi:arrow-left" className="mr-2" />
              Back to Login
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
