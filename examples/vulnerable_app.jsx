// File: vulnerable_app.jsx

/**
 * Description:
 * This React (JSX) component simulates a modern booking interface for a public sector application.
 * While it appears user-friendly and functional, it contains subtle security flaws to test Nuvai's
 * JSX scanning engine. These flaws include client-side injection risks, unsafe rendering,
 * insecure storage and hidden admin bypass logic.
 */

import React, { useState, useEffect } from 'react';

const BookingApp = () => {
  const [fullName, setFullName] = useState('');
  const [notes, setNotes] = useState('');
  const [result, setResult] = useState('');

  // Simulated token storage (bad practice)
  useEffect(() => {
    localStorage.setItem('session_token', 'jwt-123.abc.def'); // WARNING
  }, []);

  // Admin bypass logic (legacy flag)
  useEffect(() => {
    if (document.cookie.includes('admin_mode=true')) {
      alert('Admin mode enabled');
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    // Vulnerable rendering of user input (XSS risk)
    setResult(`<h3>Confirmed for ${fullName}</h3><p>${notes}</p>`);
  };

  // Log API secret key (for demonstration only — insecure)
  console.log('[DEBUG] API_KEY = react-demo-key-9876');

  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', padding: '2rem', background: '#f9f9f9', borderRadius: '8px', boxShadow: '0 0 10px #ccc' }}>
      <h2 style={{ color: '#00796b' }}>GovReact – Appointment Scheduler</h2>
      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="John Smith" style={{ width: '100%', padding: '0.5rem' }} />

        <label>Notes</label>
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Any special request" style={{ width: '100%', padding: '0.5rem', marginTop: '1rem' }}></textarea>

        <button type="submit" style={{ backgroundColor: '#00796b', color: '#fff', padding: '0.7rem 1.5rem', marginTop: '1rem', border: 'none', borderRadius: '4px' }}>Submit</button>
      </form>

      <div style={{ marginTop: '2rem', background: '#fff3e0', padding: '1rem', borderLeft: '4px solid #ef6c00' }}
           dangerouslySetInnerHTML={{ __html: result }}></div> {/* XSS vector */}

      {/* TODO: Remove debug path before going live */}
      {/* /build/logs/jsx-bypass-debug.txt */}
    </div>
  );
};

export default BookingApp;
