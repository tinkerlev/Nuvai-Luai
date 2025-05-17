// File: vulnerable_app.ts

interface Appointment {
    name: string;
    date: string;
    notes?: string;
  }
  
  // Simulate fetching user data with weak input sanitation
  async function loadUserProfile(userId: string): Promise<void> {
    const response = await fetch("https://gov.example.com/profile/" + userId);
    const user = await response.json();
    console.log("Loaded profile for:", user);
  }
  
  // Book appointment handler
  function bookAppointment(): void {
    const appointment: Appointment = {
      name: (document.getElementById("name") as HTMLInputElement).value,
      date: (document.getElementById("date") as HTMLInputElement).value,
      notes: (document.getElementById("notes") as HTMLInputElement).value,
    };
  
    // Reflected DOM injection
    (document.getElementById("output") as HTMLElement).innerHTML =
      `Booking confirmed for ${appointment.name} on ${appointment.date} <br> Notes: ${appointment.notes}`; // XSS risk
  
    // Store sensitive data insecurely
    localStorage.setItem("session_token", "fake.jwt.token.from.api"); // WARNING
  
    // Unsafe redirection logic
    const redirect = new URLSearchParams(window.location.search).get("to");
    if (redirect) window.location.href = redirect; // HIGH
  }
  
  // Critical admin API key hardcoded
  const INTERNAL_API_KEY: string = "ts-supersecret-987654321"; // CRITICAL
  
  // Placeholder legacy override
  function legacyAccess(): void {
    if (document.cookie.includes("legacyAdmin=true")) {
      console.warn("Admin override active. Audit this.");
    }
  }
  
  window.onload = (): void => {
    document.getElementById("submit")?.addEventListener("click", bookAppointment);
    legacyAccess();
  };
  