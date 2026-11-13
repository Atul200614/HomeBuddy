import React, { useState } from 'react';

export default function LeadCaptureBanner({ onBookNow }) {
  const [phone, setPhone] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (phone) {
      alert(`Thank you! HomeBuddy Pune dispatch will call ${phone} within 5 minutes.`);
      setPhone('');
    }
  };

  return (
    <div className="container" style={{ marginBottom: '4rem' }}>
      <div style={{
        background: '#0F4A3C',
        borderRadius: '24px',
        padding: '2.5rem 3rem',
        color: '#fff',
        display: 'grid',
        gridTemplateColumns: '1.2fr 0.8fr',
        gap: '2rem',
        alignItems: 'center',
        boxShadow: '0 16px 36px rgba(15, 74, 60, 0.15)'
      }}>
        <div>
          <h2 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.4rem' }}>
            Har Din Ki Safai Ka Sahara — HomeBuddy
          </h2>
          <p style={{ color: '#D1FAE5', fontSize: '0.92rem', margin: 0 }}>
            Speak to our Pune support team and schedule your cleaning today.
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '8px' }}>
          <input 
            type="tel"
            placeholder="Enter your 10-digit number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            style={{
              flex: 1,
              padding: '0.75rem 1.25rem',
              borderRadius: '9999px',
              border: 'none',
              outline: 'none',
              fontSize: '0.9rem'
            }}
            required
          />
          <button 
            type="submit"
            style={{
              background: '#EAB308',
              color: '#0A352B',
              fontWeight: 800,
              padding: '0.75rem 1.4rem',
              borderRadius: '9999px',
              border: 'none',
              fontSize: '0.9rem',
              whiteSpace: 'nowrap'
            }}
          >
            Book Now ➔
          </button>
        </form>
      </div>
    </div>
  );
}
