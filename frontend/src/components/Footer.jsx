import React from 'react';

export default function Footer() {
  return (
    <footer className="hb-site-footer">
      <div className="container">
        <div className="hb-footer-grid">
          
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#166534', color: '#fff', padding: '4px 14px', borderRadius: '9999px', fontWeight: 800, marginBottom: '1rem' }}>
              <span>🏠</span> HomeBuddy
            </div>
            <p style={{ fontSize: '0.85rem', color: '#CBD5E1', maxWidth: '320px', marginBottom: '1rem' }}>
              Expert Cleaning & Repair Solutions For Homes, Offices And Commercial Businesses across Pune.
            </p>
            <div style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
              <div style={{ fontWeight: 700, color: '#fff', marginBottom: '4px' }}>Popular Service Cities:</div>
              Mumbai | Pune | Delhi | Bengaluru | Hyderabad | Chennai | Ahmedabad | Kolkata | Lucknow | Surat
            </div>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 800, marginBottom: '1rem' }}>Company</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
              <a href="#home">Home</a>
              <a href="#services">Services</a>
              <a href="#testimonials">Testimonials</a>
              <a href="#blogs">Safety Standards</a>
              <a href="#contact">Contact Us</a>
            </div>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 800, marginBottom: '1rem' }}>Join Us</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
              <a href="#partner">Become A Partner</a>
              <a href="#careers">Technician Careers</a>
              <a href="#franchise">Business Franchise</a>
              <a href="#app">Download Partner App</a>
            </div>
          </div>

          <div>
            <h4 style={{ color: '#fff', fontSize: '0.95rem', fontWeight: 800, marginBottom: '1rem' }}>Services</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem' }}>
              <a href="#cleaning">Full House Deep Cleaning</a>
              <a href="#package">Customized Packages</a>
              <a href="#commercial">Commercial Post Interior</a>
              <a href="#emergency">Emergency Repair</a>
            </div>
          </div>

        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1.5rem', fontSize: '0.78rem', color: '#64748B', flexWrap: 'wrap', gap: '1rem' }}>
          <div>© 2026 HomeBuddy Web Application. Project by Atul Patel (TYBSc Computer Science).</div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <a href="#terms">Terms & Conditions</a>
            <a href="#privacy">Privacy Policy</a>
            <a href="#support">Helpdesk</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
