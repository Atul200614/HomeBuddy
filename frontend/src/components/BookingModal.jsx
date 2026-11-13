import React, { useState } from 'react';

export default function BookingModal({ packageData, onClose, onBookingSuccess }) {
  const [address, setAddress] = useState('Flat 402, Green Acres, Kothrud, Pune');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [slot, setSlot] = useState('10:00 AM - 12:00 PM');
  const [isEmergency, setIsEmergency] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('ONLINE');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const basePrice = packageData ? packageData.price : 5999;
  const emergencyFee = isEmergency ? 199 : 0;
  const totalPayable = basePrice + emergencyFee;

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsSubmitted(true);
    setTimeout(() => {
      onBookingSuccess({
        bookingNumber: `HB-2026-${Math.floor(10000 + Math.random() * 90000)}`,
        packageName: packageData?.name || 'Deep Home Cleaning',
        address,
        date,
        slot,
        totalPayable,
        paymentMethod
      });
    }, 800);
  };

  return (
    <div className="hb-modal-overlay" onClick={onClose}>
      <div className="hb-modal-card" onClick={(e) => e.stopPropagation()}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid #E2E8F0' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#0F4A3C', fontWeight: 800, textTransform: 'uppercase' }}>Instant Booking</span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
              {packageData?.name || 'HomeBuddy Service Booking'}
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#94A3B8' }}>✕</button>
        </div>

        {isSubmitted ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <span style={{ fontSize: '3rem' }}>🎉</span>
            <h3 style={{ fontWeight: 800, color: '#0F4A3C', marginTop: '1rem' }}>Booking Confirmed!</h3>
            <p style={{ color: '#64748B', fontSize: '0.9rem' }}>
              Your verified Pune technician has been assigned and scheduled.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                Delivery Address (Pune)
              </label>
              <input 
                type="text" 
                value={address} 
                onChange={(e) => setAddress(e.target.value)}
                style={{ width: '100%', padding: '0.6rem 0.9rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                required 
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Scheduled Date
                </label>
                <input 
                  type="date" 
                  value={date} 
                  onChange={(e) => setDate(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.9rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                  required 
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '4px' }}>
                  Arrival Time Slot
                </label>
                <select 
                  value={slot} 
                  onChange={(e) => setSlot(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.9rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                >
                  <option>08:00 AM - 10:00 AM</option>
                  <option>10:00 AM - 12:00 PM</option>
                  <option>01:00 PM - 03:00 PM</option>
                  <option>03:00 PM - 05:00 PM</option>
                  <option>05:00 PM - 07:00 PM</option>
                </select>
              </div>
            </div>

            {/* Emergency Toggle */}
            <div style={{
              background: '#FEF2F2',
              border: '1px solid #FECACA',
              borderRadius: '12px',
              padding: '0.75rem 1rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: '0.85rem', color: '#991B1B' }}>
                  ⚡ Need 45-Min Emergency Dispatch?
                </div>
                <div style={{ fontSize: '0.75rem', color: '#B91C1C' }}>
                  Priority nearby technician broadcast (+₹199)
                </div>
              </div>
              <input 
                type="checkbox" 
                checked={isEmergency}
                onChange={(e) => setIsEmergency(e.target.checked)}
                style={{ width: '18px', height: '18px', cursor: 'pointer' }}
              />
            </div>

            {/* Payment Method Choice */}
            <div>
              <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '6px' }}>
                Payment Method
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div 
                  onClick={() => setPaymentMethod('ONLINE')}
                  style={{
                    border: paymentMethod === 'ONLINE' ? '2px solid #0F4A3C' : '1px solid #CBD5E1',
                    background: paymentMethod === 'ONLINE' ? '#F0FDF4' : '#fff',
                    borderRadius: '12px',
                    padding: '0.75rem',
                    cursor: 'pointer',
                    textAlign: 'center'
                  }}
                >
                  <div style={{ fontWeight: 800, fontSize: '0.85rem', color: '#0F4A3C' }}>💳 Online (Razorpay)</div>
                  <div style={{ fontSize: '0.7rem', color: '#64748B' }}>UPI, Cards, NetBanking</div>
                </div>

                <div 
                  onClick={() => setPaymentMethod('CASH')}
                  style={{
                    border: paymentMethod === 'CASH' ? '2px solid #0F4A3C' : '1px solid #CBD5E1',
                    background: paymentMethod === 'CASH' ? '#F0FDF4' : '#fff',
                    borderRadius: '12px',
                    padding: '0.75rem',
                    cursor: 'pointer',
                    textAlign: 'center'
                  }}
                >
                  <div style={{ fontWeight: 800, fontSize: '0.85rem', color: '#0F4A3C' }}>💵 Cash on Service</div>
                  <div style={{ fontSize: '0.7rem', color: '#64748B' }}>Pay upon completion</div>
                </div>
              </div>
            </div>

            {/* Total Summary */}
            <div style={{
              background: '#F8FAFC',
              borderRadius: '12px',
              padding: '1rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginTop: '0.5rem'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748B' }}>Total Payable Amount</span>
                <div style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0F4A3C' }}>
                  ₹{totalPayable.toLocaleString('en-IN')}
                </div>
              </div>
              <button 
                type="submit"
                style={{
                  background: '#EAB308',
                  color: '#0A352B',
                  fontWeight: 800,
                  borderRadius: '9999px',
                  padding: '0.7rem 1.4rem',
                  border: 'none',
                  fontSize: '0.9rem'
                }}
              >
                Confirm Booking ➔
              </button>
            </div>

          </form>
        )}

      </div>
    </div>
  );
}
