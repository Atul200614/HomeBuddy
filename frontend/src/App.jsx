import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroBanner from './components/HeroBanner';
import TrustRibbon from './components/TrustRibbon';
import EmergencyBanner from './components/EmergencyBanner';
import CategoryGrid from './components/CategoryGrid';
import PackageCards from './components/PackageCards';
import CommercialSpaces from './components/CommercialSpaces';
import WhyChooseUs from './components/WhyChooseUs';
import HowItWorks from './components/HowItWorks';
import LeadCaptureBanner from './components/LeadCaptureBanner';
import BookingModal from './components/BookingModal';
import WorkProofModal from './components/WorkProofModal';
import Footer from './components/Footer';

export default function App() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [activePackage, setActivePackage] = useState(null);
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [showProofModal, setShowProofModal] = useState(false);
  const [bookingConfirmation, setBookingConfirmation] = useState(null);

  const handleOpenBooking = (pkg = null) => {
    setActivePackage(pkg);
    setShowBookingModal(true);
  };

  const handleBookingSuccess = (details) => {
    setBookingConfirmation(details);
    setShowBookingModal(false);
  };

  return (
    <div className="homebuddy-app">
      {/* 1. Navbar */}
      <Navbar 
        onBookClick={() => handleOpenBooking()} 
        onProofClick={() => setShowProofModal(true)}
      />

      {/* Confirmation Toast Notification if created */}
      {bookingConfirmation && (
        <div className="container" style={{ marginTop: '1rem' }}>
          <div style={{
            background: '#ECFDF5',
            border: '1px solid #A7F3D0',
            borderRadius: '16px',
            padding: '1rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 4px 12px rgba(6, 95, 70, 0.1)'
          }}>
            <div>
              <span style={{ fontWeight: 800, color: '#065F46' }}>✅ Booking #{bookingConfirmation.bookingNumber} Active!</span>
              <p style={{ margin: 0, fontSize: '0.85rem', color: '#047857' }}>
                {bookingConfirmation.packageName} scheduled for {bookingConfirmation.date} ({bookingConfirmation.slot}) at {bookingConfirmation.address}. Total: ₹{bookingConfirmation.totalPayable}.
              </p>
            </div>
            <button 
              onClick={() => setBookingConfirmation(null)}
              style={{ background: 'none', border: 'none', color: '#065F46', fontWeight: 800, fontSize: '1rem' }}
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* 2. Hero Banner */}
      <HeroBanner onBookClick={() => handleOpenBooking()} />

      {/* 3. Trust Ribbon */}
      <TrustRibbon />

      {/* 4. Emergency Express Dispatch */}
      <EmergencyBanner onEmergencyClick={() => handleOpenBooking({ name: 'Emergency Repair Express Dispatch', price: 499 })} />

      {/* 5. Category Selection Grid */}
      <CategoryGrid 
        selectedCategory={selectedCategory} 
        onSelectCategory={setSelectedCategory} 
      />

      {/* 6. Package Pricing Cards */}
      <PackageCards 
        selectedCategory={selectedCategory} 
        onSelectPackage={(pkg) => handleOpenBooking(pkg)}
      />

      {/* 7. Commercial & Corporate Spaces */}
      <CommercialSpaces onSelectService={(name) => handleOpenBooking({ name, price: 3499 })} />

      {/* 8. Why Choose Us */}
      <WhyChooseUs />

      {/* 9. How It Works Timeline */}
      <HowItWorks />

      {/* 10. Lead Capture Banner */}
      <LeadCaptureBanner onBookNow={() => handleOpenBooking()} />

      {/* 11. Footer */}
      <Footer />

      {/* Modals */}
      {showBookingModal && (
        <BookingModal 
          packageData={activePackage}
          onClose={() => setShowBookingModal(false)}
          onBookingSuccess={handleBookingSuccess}
        />
      )}

      {showProofModal && (
        <WorkProofModal 
          onClose={() => setShowProofModal(false)}
        />
      )}
    </div>
  );
}
