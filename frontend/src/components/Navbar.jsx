import React, { useState } from 'react';

export default function Navbar({ onBookClick, onProofClick }) {
  const [addressMode, setAddressMode] = useState('home');
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <header className="hb-header">
      <div className="container">
        <div className="hb-nav-inner">
          
          {/* Logo & Location */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="hb-logo">
              <span style={{ color: '#EAB308' }}>🏠</span>
              <span>HomeBuddy</span>
            </div>

            {/* Location Selector (Pune, Maharashtra - Home/Office) */}
            <div className="hb-loc-pill">
              <span style={{ color: '#EF4444' }}>📍</span>
              <span>Pune, Maharashtra</span>
              <div style={{ display: 'flex', gap: '4px', marginLeft: '6px' }}>
                <span 
                  className={`hb-mode-badge ${addressMode === 'home' ? 'active' : ''}`}
                  onClick={() => setAddressMode('home')}
                  style={{ cursor: 'pointer' }}
                >
                  Home
                </span>
                <span 
                  className={`hb-mode-badge ${addressMode === 'office' ? 'active' : ''}`}
                  onClick={() => setAddressMode('office')}
                  style={{ cursor: 'pointer' }}
                >
                  Office
                </span>
              </div>
            </div>
          </div>

          {/* Search Bar */}
          <div className="hb-search-bar">
            <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94A3B8' }}>🔍</span>
            <input 
              type="text" 
              placeholder="Search for deep cleaning, electrician, plumbing..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <a href="tel:07971123101" style={{ fontSize: '0.88rem', fontWeight: 600, color: '#475569', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <span>📞</span> 07971123101
            </a>

            <button className="hb-btn-cta" onClick={() => onBookClick()}>
              <span>📅</span> Book A Service
            </button>

            <button 
              onClick={() => onProofClick()}
              style={{
                background: '#ECFDF5',
                color: '#065F46',
                border: '1px solid #A7F3D0',
                borderRadius: '9999px',
                padding: '0.45rem 0.9rem',
                fontSize: '0.8rem',
                fontWeight: 700
              }}
            >
              📸 Work Proofs
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
