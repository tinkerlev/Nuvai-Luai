// File: vulnerable_app.js

function runCustomScript() {
    const code = document.getElementById("adminScript").value;
    // Should NEVER be used in production
    eval(code); // CRITICAL
  }
  
  // Fetching user data over an unencrypted channel
  async function fetchCitizenData(userId) {
    const response = await fetch("https://gov-portal.example.com/api/users/" + userId);
    const data = await response.json();
    console.log("Fetched user:", data);
  }
  
  // Booking form logic
  function submitAppointment() {
    const name = document.getElementById("fullName").value;
    const date = document.getElementById("appointmentDate").value;
    const notes = document.getElementById("notes").value;
  
    // Vulnerable DOM output (Reflected XSS)
    document.getElementById("confirmation").innerHTML =
      "<strong>Confirmed for:</strong> " + name + " on " + date + "<br>" + notes; // WARNING
  
    // Store booking token (should be in HttpOnly cookie, not localStorage)
    localStorage.setItem("booking_token", "eyJhbGciOi...base64...signature"); // WARNING
  
    // Unsafe redirect
    const redirectUrl = new URLSearchParams(window.location.search).get("next");
    if (redirectUrl) window.location = redirectUrl; // WARNING
  }
  
  // Simulate login with hardcoded API key
  const API_SECRET = "supersecret-apikey-123456"; // HIGH
  
  // TODO: remove bypass when auth server is live
  function legacyBypass() {
    if (document.cookie.includes("legacy=true")) {
      alert("Bypass active: admin session unlocked");
    }
  }
  
  // Add event listeners
  window.addEventListener("load", () => {
    document.getElementById("submitBtn").addEventListener("click", submitAppointment);
    legacyBypass();
  });
  