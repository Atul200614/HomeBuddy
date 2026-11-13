// HomeBuddy Main Client Script
document.addEventListener('DOMContentLoaded', () => {
    // 1. Location Type Switcher (Home / Office)
    const pills = document.querySelectorAll('.hb-type-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', (e) => {
            pills.forEach(p => p.classList.remove('active'));
            e.currentTarget.classList.add('active');
            const mode = e.currentTarget.dataset.mode;
            localStorage.setItem('hb_address_mode', mode);
        });
    });

    // 2. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // 3. Dynamic Emergency Booking Fee Calculation
    const emergencyCheckbox = document.getElementById('id_is_emergency');
    const totalDisplay = document.getElementById('hb-total-display');
    if (emergencyCheckbox && totalDisplay) {
        const basePrice = parseFloat(totalDisplay.dataset.basePrice || '0');
        const emergencySurcharge = parseFloat(totalDisplay.dataset.emergencyFee || '199');
        
        emergencyCheckbox.addEventListener('change', () => {
            let total = basePrice;
            if (emergencyCheckbox.checked) {
                total += emergencySurcharge;
            }
            totalDisplay.textContent = `₹${total.toFixed(2)}`;
        });
    }
});
