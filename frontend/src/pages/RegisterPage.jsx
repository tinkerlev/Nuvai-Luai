// file: RegisterPage.jsx

import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Icon } from '@iconify/react';

export default function RegisterPage() {
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    profession: "",
    company: "",
    plan: "monthly"
  });
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastSubmitTime, setLastSubmitTime] = useState(0);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const navigate = useNavigate();

  const sanitizeInput = (input) => input.replace(/[<>"']/g, "").normalize("NFKC");
  const escapeHTML = (str) => str.replace(/</g, "&lt;").replace(/>/g, "&gt;");

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) && !email.endsWith("@example.com");
  const validatePhone = (phone) => /^[0-9]{7,15}$/.test(phone);
  const isAlphaOnly = (text) => /^[a-zA-Z\-'\s]{1,50}$/.test(text);

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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: sanitizeInput(value) }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!acceptTerms) {
      setErrorMsg("Please accept the terms and conditions");
      return;
    }
    setErrorMsg("");

    const COOLDOWN_MS = 10000;
    if (Date.now() - lastSubmitTime < COOLDOWN_MS) {
      setErrorMsg("Please wait before trying again.");
      return;
    }
    setLastSubmitTime(Date.now());

    if (!isAlphaOnly(form.firstName) || !isAlphaOnly(form.lastName)) {
      setErrorMsg("Names must contain only letters and basic characters.");
      return;
    }
    if (!validateEmail(form.email)) {
      setErrorMsg("Invalid email address.");
      return;
    }
    if (!validatePhone(form.phone)) {
      setErrorMsg("Invalid phone number.");
      return;
    }
    if (!validatePassword(form.password)) {
      setErrorMsg("Password must be 12+ chars, include upper/lowercase, number, special character.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);

      const csrfToken = localStorage.getItem("csrfToken") || "";

      const apiUrl = process.env.REACT_APP_API_URL;
      console.log("API URL:", apiUrl);
      const res = await fetch(`${apiUrl}/auth/register`, {

        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRF-Token": csrfToken,
        },
        credentials: "include",
        body: JSON.stringify(form),
        signal: controller.signal,
      });

      clearTimeout(timeout);

      if (!res.ok) {
        const errData = await res.json();
        setErrorMsg(escapeHTML(errData.message || "Registration failed."));
        setLoading(false);
        return;
      }

      navigate("/login");
    } catch (err) {
      if (err.name === "AbortError") {
        setErrorMsg("Request timed out. Please try again.");
      } else {
        console.error("Register error:", err);
        setErrorMsg("Unexpected error. Try again later.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fadeIn = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.1 } }
  };

  const staggerItems = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const formItem = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen bg-base-200 flex items-center justify-center p-4 py-10">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeIn}
        className="w-full max-w-lg"
      >
        <div className="card w-full bg-base-100 shadow-xl border border-base-300">
          <div className="card-body">
            <div className="flex justify-center mb-2">
              <div className="w-16 h-16 rounded-full bg-secondary/10 flex items-center justify-center">
                <Icon icon="mdi:account-plus" className="w-8 h-8 text-secondary"/>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-center mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Create Your Account
            </h2>

            <form onSubmit={handleSubmit}>
              <motion.div variants={staggerItems}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <motion.div variants={formItem} className="form-control">
                    <label className="label">
                      <span className="label-text">First Name</span>
                    </label>
                    <input
                      type="text"
                      name="firstName"
                      placeholder="First Name"
                      value={form.firstName}
                      onChange={handleChange}
                      className="input input-bordered w-full"
                      maxLength={50}
                      required
                      autoComplete="off"
                    />
                  </motion.div>
                  
                  <motion.div variants={formItem} className="form-control">
                    <label className="label">
                      <span className="label-text">Last Name</span>
                    </label>
                    <input
                      type="text"
                      name="lastName"
                      placeholder="Last Name"
                      value={form.lastName}
                      onChange={handleChange}
                      className="input input-bordered w-full"
                      maxLength={50}
                      required
                      autoComplete="off"
                    />
                  </motion.div>
                </div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Email</span>
                  </label>
                  <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    value={form.email}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    maxLength={50}
                    required
                    autoComplete="off"
                  />
                </motion.div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Phone Number</span>
                  </label>
                  <input
                    type="text"
                    name="phone"
                    placeholder="Phone Number"
                    value={form.phone}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    maxLength={15}
                    required
                    autoComplete="off"
                  />
                </motion.div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <motion.div variants={formItem} className="form-control">
                    <label className="label">
                      <span className="label-text">Profession</span>
                    </label>
                    <input
                      type="text"
                      name="profession"
                      placeholder="Profession"
                      value={form.profession}
                      onChange={handleChange}
                      className="input input-bordered w-full"
                      maxLength={50}
                      required
                      autoComplete="off"
                    />
                  </motion.div>
                  
                  <motion.div variants={formItem} className="form-control">
                    <label className="label">
                      <span className="label-text">Company (Optional)</span>
                    </label>
                    <input
                      type="text"
                      name="company"
                      placeholder="Company"
                      value={form.company}
                      onChange={handleChange}
                      className="input input-bordered w-full"
                      maxLength={50}
                      autoComplete="off"
                    />
                  </motion.div>
                </div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Password</span>
                  </label>
                  <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={form.password}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                    maxLength={100}
                    autoComplete="new-password"
                  />
                  <label className="label">
                    <span className="label-text-alt">Must be at least 12 characters with letters, numbers and symbols</span>
                  </label>
                </motion.div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Confirm Password</span>
                  </label>
                  <input
                    type="password"
                    name="confirmPassword"
                    placeholder="Confirm Password"
                    value={form.confirmPassword}
                    onChange={handleChange}
                    className="input input-bordered w-full"
                    required
                    maxLength={100}
                    autoComplete="new-password"
                  />
                </motion.div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label">
                    <span className="label-text">Subscription Plan</span>
                  </label>
                  <select
                    name="plan"
                    value={form.plan}
                    onChange={handleChange}
                    className="select select-bordered w-full"
                  >
                    <option value="monthly">📆 Monthly Plan</option>
                    <option value="yearly">📅 Yearly Plan</option>
                    <option value="business">🏢 Business Plan</option>
                  </select>
                </motion.div>
                
                <motion.div variants={formItem} className="form-control mb-4">
                  <label className="label cursor-pointer justify-start gap-2">
                    <input 
                      type="checkbox" 
                      className="checkbox checkbox-sm checkbox-secondary" 
                      checked={acceptTerms}
                      onChange={() => setAcceptTerms(!acceptTerms)}
                    />
                    <span className="label-text">I agree to the Terms of Service and Privacy Policy</span>
                  </label>
                </motion.div>
              </motion.div>
              
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
              
              <button
                type="submit"
                disabled={loading || !acceptTerms}
                className={`btn btn-secondary w-full ${loading ? "loading" : ""}`}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="loading loading-spinner loading-sm mr-2"></span>
                    Creating Account...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Icon icon="mdi:account-check" className="mr-2" />
                    Create Account
                  </span>
                )}
              </button>
            </form>
            
            <div className="divider my-4"></div>
            
            <div className="text-center">
              <p className="text-sm">
                Already have an account?{" "}
                <Link to="/login" className="link link-secondary">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
