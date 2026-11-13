import React from 'react';

export default function HeroBanner({ onBookClick }) {
  return (
    <div className="container">
      <div className="hb-hero">
        <div>
          <div className="hb-hero-badge">
            ✨ FESTIVAL SPECIAL OFFER
          </div>
          <h1>
            Deep Home Cleaning <span>Reinvented.</span>
          </h1>
          <p>
            Get your home sanitized and spotless with eco-friendly products and certified 5-star professional cleaners in Pune.
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
            <button className="hb-btn-cta" style={{ padding: '0.75rem 1.75rem', fontSize: '1rem' }} onClick={() => onBookClick()}>
              Book Deep Cleaning ➔
            </button>
            <span style={{
              background: 'rgba(0,0,0,0.3)',
              color: '#FDE047',
              border: '1px solid rgba(253, 224, 71, 0.3)',
              borderRadius: '9999px',
              padding: '0.45rem 1rem',
              fontSize: '0.82rem',
              fontWeight: 600
            }}>
              ⏳ Valid till Nov 30, 2026
            </span>
          </div>
        </div>

        {/* Hero Graphic Card */}
        <div className="hb-hero-card">
          <img 
            src="https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=700&q=80" 
            alt="Spotless Clean Living Room" 
          />
          <div className="hb-satisfaction-pill">
            <span style={{ fontSize: '1.25rem' }}>🛡️</span>
            <div>
              <div style={{ fontWeight: 800 }}>Satisfaction 100%</div>
              <div style={{ fontSize: '0.7rem', opacity: 0.8 }}>Guaranteed Service</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
