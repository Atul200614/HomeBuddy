import React from 'react';
import { featuredPackages } from '../data/mockData';

export default function PackageCards({ selectedCategory, onSelectPackage }) {
  const filtered = selectedCategory 
    ? featuredPackages.filter(p => p.category === selectedCategory)
    : featuredPackages;

  return (
    <div className="container">
      <div className="hb-section-head">
        <div>
          <h2>Full House Deep Cleaning & Packages</h2>
          <p style={{ color: '#64748B', fontSize: '0.9rem' }}>A complete deep clean for a fresher, healthier home.</p>
        </div>
      </div>

      <div className="hb-cards-grid">
        {filtered.map((pkg) => (
          <div key={pkg.id} className="hb-pkg-card">
            <img src={pkg.image} alt={pkg.name} className="hb-pkg-img" />
            <div className="hb-pkg-body">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{
                  background: '#ECFDF5',
                  color: '#065F46',
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  padding: '2px 8px',
                  borderRadius: '9999px'
                }}>
                  {pkg.tag}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#64748B' }}>⏱️ {pkg.duration}</span>
              </div>

              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, marginBottom: '4px' }}>{pkg.name}</h3>
              <p style={{ fontSize: '0.8rem', color: '#64748B', marginBottom: '8px', fontWeight: 600 }}>{pkg.sqft}</p>
              <p style={{ fontSize: '0.82rem', color: '#475569', flex: 1, marginBottom: '16px' }}>{pkg.description}</p>

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '12px',
                borderTop: '1px solid #E2E8F0',
                marginTop: 'auto'
              }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: '#94A3B8' }}>Starts at</div>
                  <div className="hb-pkg-price">₹{pkg.price.toLocaleString('en-IN')}</div>
                </div>

                <button 
                  onClick={() => onSelectPackage(pkg)}
                  style={{
                    background: '#0F4A3C',
                    color: '#fff',
                    fontWeight: 700,
                    borderRadius: '9999px',
                    padding: '0.5rem 1.2rem',
                    border: 'none',
                    fontSize: '0.85rem'
                  }}
                >
                  Book Service
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
