import React, { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [passwordScore, setPasswordScore] = useState(0);
  const navigate = useNavigate();

  const sanitizeInput = (input) => input.replace(/[<>"']/g, "").normalize("NFKC");

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
    setErrorMsg("");
    setSuccessMsg("");

    const cleanPassword = sanitizeInput(password);
    const cleanConfirm = sanitizeInput(confirmPassword);

    if (!validatePassword(cleanPassword)) {
      setErrorMsg("Password does not meet security requirements.");
      return;
    }

    if (cleanPassword !== cleanConfirm) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/auth/reset-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({ token, password: cleanPassword }),
      });

      if (!res.ok) {
        const data = await res.json();
        setErrorMsg(data.message || "Reset failed. Try again.");
        setLoading(false);
        return;
      }

      setSuccessMsg("✅ Password reset successful. Redirecting to login...");
      setTimeout(() => navigate("/login"), 3000);
    } catch (err) {
      console.error("Reset error:", err);
      setErrorMsg("Unexpected error. Please try again.");
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
              <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center">
                <Icon icon="mdi:shield-key" className="w-8 h-8 text-success"/>
              </div>
            </div>
            
            <h2 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-success to-accent bg-clip-text text-transparent">
              Reset Your Password
            </h2>
            
            <p className="text-center text-base-content/80 mb-6">
              Please create a strong, unique password for your account.
            </p>
            
            <form onSubmit={handleSubmit}>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">New Password</span>
                </label>
                <input
                  type="password"
                  placeholder="New Password"
                  value={password}
                  onChange={(e) => handlePasswordChange(e.target.value)}
                  className="input input-bordered w-full"
                  required
                  maxLength={100}
                  autoComplete="new-password"
                />
                {password && (
                  <div className="mt-2">
                    <progress 
                      className={`progress w-full ${
                        passwordScore >= 5 ? "progress-success" : 
                        passwordScore >= 3 ? "progress-warning" : "progress-error"
                      }`} 
                      value={passwordScore} 
                      max="5"
                    ></progress>
                    <label className="label">
                      <span className="label-text-alt">Password strength: {passwordScore}/5</span>
                    </label>
                  </div>
                )}
              </div>
              
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Confirm New Password</span>
                </label>
                <input
                  type="password"
                  placeholder="Confirm New Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`input input-bordered w-full ${
                    confirmPassword && confirmPassword !== password ? "input-error" : ""
                  }`}
                  required
                  maxLength={100}
                  autoComplete="new-password"
                />
                {confirmPassword && confirmPassword !== password && (
                  <label className="label">
                    <span className="label-text-alt text-error">Passwords don't match</span>
                  </label>
                )}
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
              
              {successMsg && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="alert alert-success mb-4"
                >
                  <Icon icon="mdi:check-circle" className="h-6 w-6" />
                  <span>{successMsg}</span>
                </motion.div>
              )}
              
              <button
                type="submit"
                disabled={loading || password !== confirmPassword}
                className={`btn btn-success w-full ${loading ? "loading" : ""}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Setting Password...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Icon icon="mdi:check-shield" className="mr-2" />
                    Set New Password
                  </span>
                )}
              </button>
            </form>
            
            <div className="divider my-4"></div>
            
            <div className="text-center">
              <Link to="/login" className="link link-secondary">
                Return to login
              </Link>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
