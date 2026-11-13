import React from 'react';

export default function WhyChooseUs() {
  const points = [
    { icon: '🛡️', title: 'Trusted Followers', desc: '10,000+ satisfied households served' },
    { icon: '👨‍🔧', title: 'Pro Level Teams', desc: 'Police verified & certified technicians' },
    { icon: '😊', title: 'Happy Clients', desc: '4.9/5 average service satisfaction rating' },
    { icon: '🔔', title: 'Service Reminders', desc: 'Automated SMS, in-app & arrival alerts' },
    { icon: '⚡', title: 'Fast, Flexible, Hustle Free', desc: 'Seamless 2-hour arrival scheduling' },
    { icon: '🏢', title: 'From Homes To Offices', desc: 'Tailored residential & commercial care' },
  ];

  return (
    <div className="container" style={{ marginBottom: '3.5rem' }}>
      <div style={{
        background: '#fff',
        borderRadius: '24px',
        padding: '3rem',
        border: '1px solid #E2E8F0',
        boxShadow: 'var(--hb-shadow)',
        display: 'grid',
        gridTemplateColumns: '1.2fr 0.8fr',
        gap: '2.5rem',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', color: '#0F172A' }}>
            WHY CHOOSE US
          </h2>
          <p style={{ color: '#64748B', fontSize: '0.92rem', marginBottom: '2rem' }}>
            Choose from our most booked cleaning packages, designed for every home and space in Pune.
          </p>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.25rem'
          }}>
            {points.map((p, i) => (
              <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
                <span style={{ fontSize: '1.4rem' }}>{p.icon}</span>
                <div>
                  <div style={{ fontWeight: 800, fontSize: '0.92rem', color: '#0F172A' }}>{p.title}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{p.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          <img 
            src="https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?auto=format&fit=crop&w=700&q=80" 
            alt="Professional cleaner in uniform" 
            style={{ width: '100%', height: '340px', objectFit: 'cover', borderRadius: '20px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}
          />
        </div>
      </div>
    </div>
  );
}
