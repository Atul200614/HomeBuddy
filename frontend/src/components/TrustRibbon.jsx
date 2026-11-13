import React from 'react';

export default function TrustRibbon() {
  const points = [
    { icon: '🎖️', title: 'ISO 9001:2015 Certified', sub: 'Cleaning Service' },
    { icon: '👥', title: '100% Background-Checked', sub: 'Verified Staff' },
    { icon: '⭐', title: 'Trained & Professional', sub: 'Dedicated Teams' },
    { icon: '🌿', title: 'Eco-Friendly', sub: 'Cleaning Products' },
  ];

  return (
    <div className="container">
      <div className="hb-trust-bar">
        {points.map((p, i) => (
          <div key={i} className="hb-trust-box">
            <div className="hb-trust-ico">{p.icon}</div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.88rem' }}>{p.title}</div>
              <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{p.sub}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
