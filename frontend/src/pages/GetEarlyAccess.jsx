// file: GetEarlyAccess.jsx

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Icon } from "@iconify/react";

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

export default function GetEarlyAccess() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    birthDate: "",
    location: "",
  });
  const [message, setMessage] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const sanitize = (text) =>
    text.replace(/[<>"'`;]/g, "").normalize("NFKC").trim();

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: sanitize(e.target.value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    setErrorMsg("");

    const { firstName, lastName, email, birthDate } = formData;
    if (!firstName || !lastName || !email || !birthDate) {
      setErrorMsg("Please fill in all required fields.");
      return;
    }

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailValid) {
      setErrorMsg("Invalid email address.");
      return;
    }

    const birth = new Date(birthDate);
    const age = new Date().getFullYear() - birth.getFullYear();
    if (age < 16) {
      setErrorMsg("You must be at least 16 years old to sign up.");
      return;
    }

    setLoading(true);
    try {
      const API_BASE = import.meta.env.REACT_APP_API_BASE_URL;
      const res = await fetch(`${API_BASE}/api/early-access`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
        body: JSON.stringify({
          first_name: firstName,
          last_name: lastName,
          email: email,
          birth_date: birthDate,
          location: formData.location,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Signup failed.");
      }

      setMessage(data.message || "✅ You're on the list! Thank you.");
      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        birthDate: "",
        location: "",
      });
    } catch (err) {
      setErrorMsg(err.message || "Unexpected error. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-base-200 flex items-center justify-center p-6">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={fadeIn}
        className="w-full max-w-md"
      >
        <div className="card bg-base-100 shadow-xl border border-base-300">
          <div className="card-body">
            <h2 className="text-2xl font-bold text-center mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Get Early Access
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="form-control mb-3">
                <label className="label">
                  <span className="label-text">First Name</span>
                </label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control mb-3">
                <label className="label">
                  <span className="label-text">Last Name</span>
                </label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control mb-3">
                <label className="label">
                  <span className="label-text">Email</span>
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control mb-3">
                <label className="label">
                  <span className="label-text">Birth Date</span>
                </label>
                <input
                  type="date"
                  name="birthDate"
                  value={formData.birthDate}
                  onChange={handleChange}
                  className="input input-bordered"
                  required
                />
              </div>
              <div className="form-control mb-4">
                <label className="label">
                  <span className="label-text">Location </span>
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  className="input input-bordered"
                />
              </div>
              {errorMsg && (
                <div className="alert alert-error mb-4">
                  <Icon icon="mdi:alert-circle" className="h-6 w-6" />
                  <span>{errorMsg}</span>
                </div>
              )}
              {message && (
                <div className="alert alert-success mb-4">
                  <Icon icon="mdi:check-circle" className="h-6 w-6" />
                  <span>{message}</span>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className={`btn btn-primary w-full ${loading ? "loading" : ""}`}
              >
                {loading ? "Submitting..." : "Join the Waitlist"}
              </button>
            </form>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
