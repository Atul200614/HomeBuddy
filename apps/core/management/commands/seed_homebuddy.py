import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.customers.models import CustomerProfile, Address
from apps.professionals.models import ProviderProfile, ProviderSkill, VerificationDocument
from apps.services.models import Category, Service, ProviderService
from apps.bookings.models import Booking, BookingStatusHistory, WorkProof
from apps.payments.models import Payment, EarningsLedger, Invoice
from apps.reviews.models import Review
from apps.complaints.models import Complaint
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = "Seed database with realistic HomeBuddy demonstration data (Pune location)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting HomeBuddy database seed..."))

        # 1. Platform Admin
        admin_user, _ = User.objects.get_or_create(
            email='admin@homebuddy.local',
            defaults={
                'username': 'admin@homebuddy.local',
                'first_name': 'Atul',
                'last_name': 'Patel',
                'phone': '9876543210',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.save()

        # 2. Customers
        c1, _ = User.objects.get_or_create(
            email='rahul.sharma@example.com',
            defaults={
                'username': 'rahul.sharma@example.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'phone': '9123456780',
                'role': 'CUSTOMER'
            }
        )
        c1.set_password('Customer@123')
        c1.save()
        c1_prof, _ = CustomerProfile.objects.get_or_create(user=c1)
        addr1, _ = Address.objects.get_or_create(
            user=c1,
            title='Home',
            defaults={
                'address_line1': 'Flat 402, Green Acres Residency',
                'address_line2': 'Kothrud',
                'landmark': 'Near Vanaz Metro Station',
                'city': 'Pune',
                'state': 'Maharashtra',
                'pincode': '411038',
                'is_default': True
            }
        )

        c2, _ = User.objects.get_or_create(
            email='sneha.patil@example.com',
            defaults={
                'username': 'sneha.patil@example.com',
                'first_name': 'Sneha',
                'last_name': 'Patil',
                'phone': '9123456781',
                'role': 'CUSTOMER'
            }
        )
        c2.set_password('Customer@123')
        c2.save()
        c2_prof, _ = CustomerProfile.objects.get_or_create(user=c2)
        addr2, _ = Address.objects.get_or_create(
            user=c2,
            title='Office',
            defaults={
                'address_line1': 'Unit 301, Prime Business Bay',
                'address_line2': 'Baner-Pashan Link Road',
                'landmark': 'Opposite High Street Cafe',
                'city': 'Pune',
                'state': 'Maharashtra',
                'pincode': '411045',
                'is_default': True
            }
        )

        # 3. Service Providers / Technicians
        # Provider 1: Suresh Deep Cleaning
        p1_user, _ = User.objects.get_or_create(
            email='suresh.cleaner@example.com',
            defaults={
                'username': 'suresh.cleaner@example.com',
                'first_name': 'Suresh',
                'last_name': 'Jadhav',
                'phone': '9822012345',
                'role': 'PROVIDER'
            }
        )
        p1_user.set_password('Provider@123')
        p1_user.save()
        p1_prof, _ = ProviderProfile.objects.get_or_create(
            user=p1_user,
            defaults={
                'business_name': 'Suresh Safaiwala & Deep Cleaners',
                'bio': 'Over 8 years experience in residential deep cleaning, mechanized floor scrubbing, and post-interior paint cleaning.',
                'experience_years': 8,
                'is_verified': True,
                'verification_date': timezone.now(),
                'avg_rating': Decimal('4.90'),
                'total_reviews': 38,
                'total_jobs_completed': 64,
                'service_city': 'Pune',
                'service_pincodes': '411038, 411045, 411057, 411014'
            }
        )
        ProviderSkill.objects.get_or_create(provider=p1_prof, skill_name='Kitchen Degreasing', years_experience=6)
        ProviderSkill.objects.get_or_create(provider=p1_prof, skill_name='Mechanized Floor Buffing', years_experience=8)

        # Provider 2: Vikram Electrician
        p2_user, _ = User.objects.get_or_create(
            email='vikram.electric@example.com',
            defaults={
                'username': 'vikram.electric@example.com',
                'first_name': 'Vikram',
                'last_name': 'Shinde',
                'phone': '9822054321',
                'role': 'PROVIDER'
            }
        )
        p2_user.set_password('Provider@123')
        p2_user.save()
        p2_prof, _ = ProviderProfile.objects.get_or_create(
            user=p2_user,
            defaults={
                'business_name': 'Vikram Certified Electrical Services',
                'bio': 'Licensed wireman certified by Maharashtra Electrical Inspectorate. Specialized in MCB tripping, inverter wiring, and light fittings.',
                'experience_years': 6,
                'is_verified': True,
                'verification_date': timezone.now(),
                'avg_rating': Decimal('4.85'),
                'total_reviews': 24,
                'total_jobs_completed': 42,
                'service_city': 'Pune',
                'service_pincodes': '411038, 411004, 411007'
            }
        )
        ProviderSkill.objects.get_or_create(provider=p2_prof, skill_name='MCB & Distribution Box Wiring', years_experience=6)

        # Provider 3: Mahesh Plumber
        p3_user, _ = User.objects.get_or_create(
            email='mahesh.plumber@example.com',
            defaults={
                'username': 'mahesh.plumber@example.com',
                'first_name': 'Mahesh',
                'last_name': 'More',
                'phone': '9822098765',
                'role': 'PROVIDER'
            }
        )
        p3_user.set_password('Provider@123')
        p3_user.save()
        p3_prof, _ = ProviderProfile.objects.get_or_create(
            user=p3_user,
            defaults={
                'business_name': 'Mahesh Rapid Plumbing Solutions',
                'bio': 'Specialized in bathroom sanitary fixtures, drain unclogging, water tank pipeline connections, and leak sealing.',
                'experience_years': 5,
                'is_verified': True,
                'verification_date': timezone.now(),
                'avg_rating': Decimal('5.00'),
                'total_reviews': 18,
                'total_jobs_completed': 35,
                'service_city': 'Pune',
                'service_pincodes': '411038, 411029, 411052'
            }
        )

        # 4. Service Categories
        cat_clean, _ = Category.objects.get_or_create(
            slug='cleaning',
            defaults={'name': 'Deep Cleaning', 'icon_name': 'bi-droplet-half', 'display_order': 1}
        )
        cat_electric, _ = Category.objects.get_or_create(
            slug='electrical',
            defaults={'name': 'Electrician', 'icon_name': 'bi-lightning-charge', 'display_order': 2}
        )
        cat_plumb, _ = Category.objects.get_or_create(
            slug='plumbing',
            defaults={'name': 'Plumber', 'icon_name': 'bi-wrench', 'display_order': 3}
        )
        cat_carpenter, _ = Category.objects.get_or_create(
            slug='carpentry',
            defaults={'name': 'Carpenter', 'icon_name': 'bi-hammer', 'display_order': 4}
        )
        cat_paint, _ = Category.objects.get_or_create(
            slug='painting',
            defaults={'name': 'Painting', 'icon_name': 'bi-brush', 'display_order': 5}
        )
        cat_cook, _ = Category.objects.get_or_create(
            slug='cooking',
            defaults={'name': 'Cook & Chef', 'icon_name': 'bi-egg-fried', 'display_order': 6}
        )

        # 5. Services Catalog
        s1, _ = Service.objects.get_or_create(
            slug='2-bhk-deep-cleaning',
            defaults={
                'category': cat_clean,
                'name': '2 BHK Full House Deep Cleaning',
                'short_description': 'Upto 800 sq.ft comprehensive mechanized cleaning, kitchen degreasing, bathroom scrubbing, floor buffing & balcony.',
                'detailed_description': 'Our standardized 5-star cleaning process includes: 1) Thorough kitchen degreasing, cabinet interior/exterior wiping; 2) Bathroom descaling and acid-safe tile polishing; 3) Heavy mechanized single-disc scrubbing on all tile/marble floors; 4) Balcony and window grill pressure wiping; 5) Dry vacuuming of all sofa and mattress furnishings.',
                'pricing_type': 'PACKAGE',
                'base_price': Decimal('5999.00'),
                'estimated_duration_minutes': 240,
                'is_emergency_eligible': False
            }
        )

        s2, _ = Service.objects.get_or_create(
            slug='3-bhk-deep-cleaning',
            defaults={
                'category': cat_clean,
                'name': '3 BHK Full House Deep Cleaning',
                'short_description': 'Upto 1200 sq.ft complete home sanitation and mechanized deep scrubbing for large apartments.',
                'detailed_description': 'Comprehensive 3-BHK home deep clean covering 3 bathrooms, kitchen exhaust & slab cleaning, terrace washing, interior windows, and room sanitation with eco-friendly Diversey chemicals.',
                'pricing_type': 'PACKAGE',
                'base_price': Decimal('6999.00'),
                'estimated_duration_minutes': 360,
                'is_emergency_eligible': False
            }
        )

        s3, _ = Service.objects.get_or_create(
            slug='electrical-repair-switchboard',
            defaults={
                'category': cat_electric,
                'name': 'Fan & Switchboard Electrical Repair',
                'short_description': 'Fix sparking switches, ceiling fan regulators, socket shorts, and lighting fixtures.',
                'detailed_description': 'Professional diagnosis with multimeter testing, wire gauge verification, replacement of burnt switch components, and safe earthing inspection.',
                'pricing_type': 'FIXED',
                'base_price': Decimal('299.00'),
                'estimated_duration_minutes': 45,
                'is_emergency_eligible': True,
                'emergency_surcharge': Decimal('149.00')
            }
        )

        s4, _ = Service.objects.get_or_create(
            slug='drain-leakage-plumbing',
            defaults={
                'category': cat_plumb,
                'name': 'Drain Unclogging & Tap Leak Fix',
                'short_description': 'Clear jammed kitchen sinks, bathroom floor drains, and dripping mixer taps.',
                'detailed_description': 'Rotary snake wire drain clearing, washer replacement, silicone waterproofing of joint seams, and water pressure alignment.',
                'pricing_type': 'FIXED',
                'base_price': Decimal('349.00'),
                'estimated_duration_minutes': 60,
                'is_emergency_eligible': True,
                'emergency_surcharge': Decimal('199.00')
            }
        )

        # 6. Sample Bookings in Realistic Workflows
        # Booking 1: Completed with work proof, review, invoice, and ledger
        today = datetime.date.today()
        b1, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00101',
            defaults={
                'customer': c1_prof,
                'provider': p1_prof,
                'service': s1,
                'address': addr1,
                'scheduled_date': today - datetime.timedelta(days=2),
                'time_slot': '10:00 AM - 12:00 PM',
                'status': 'COMPLETED',
                'service_price': Decimal('5999.00'),
                'total_amount': Decimal('5999.00'),
                'special_instructions': 'Flat has hardwood in bedroom and vitrified tiles in hall.'
            }
        )
        WorkProof.objects.get_or_create(
            booking=b1,
            defaults={
                'before_photo': 'work_proofs/before/sample_before.jpg',
                'after_photo': 'work_proofs/after/sample_after.jpg',
                'work_notes': 'Completely scrubbed bathroom tiles, degreased kitchen chimney, and buffed living room floors.',
                'customer_confirmed': True,
                'customer_confirmed_at': timezone.now() - datetime.timedelta(days=2),
                'customer_feedback': 'Exceptional cleaning quality! Every corner looks spotless.'
            }
        )
        Payment.objects.get_or_create(
            booking=b1,
            defaults={
                'amount': Decimal('5999.00'),
                'payment_method': 'ONLINE_RAZORPAY',
                'status': 'SUCCESS',
                'razorpay_payment_id': 'pay_demo_success_101',
                'razorpay_order_id': 'order_HB_2026_00101'
            }
        )
        EarningsLedger.objects.get_or_create(
            booking=b1,
            defaults={
                'provider': p1_prof,
                'gross_amount': Decimal('5999.00'),
                'commission_rate': Decimal('10.00'),
                'commission_amount': Decimal('599.90'),
                'net_earnings': Decimal('5399.10')
            }
        )
        Invoice.objects.get_or_create(
            booking=b1,
            defaults={
                'invoice_number': 'INV-2026-00101',
                'subtotal': Decimal('5999.00'),
                'total_amount': Decimal('5999.00')
            }
        )
        Review.objects.get_or_create(
            booking=b1,
            defaults={
                'customer': c1_prof,
                'provider': p1_prof,
                'rating': 5,
                'review_text': 'Suresh and his team were polite, on time, and performed an outstanding cleaning job. Highly recommended!'
            }
        )

        # Booking 2: Work Proof Submitted (Ready for customer confirmation)
        b2, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00102',
            defaults={
                'customer': c2_prof,
                'provider': p2_prof,
                'service': s3,
                'address': addr2,
                'scheduled_date': today,
                'time_slot': '02:00 PM - 04:00 PM',
                'status': 'WORK_PROOF_SUBMITTED',
                'service_price': Decimal('299.00'),
                'total_amount': Decimal('299.00'),
                'special_instructions': 'Main hall light socket sparking.'
            }
        )
        WorkProof.objects.get_or_create(
            booking=b2,
            defaults={
                'before_photo': 'work_proofs/before/sample_switch.jpg',
                'after_photo': 'work_proofs/after/sample_switch_fixed.jpg',
                'work_notes': 'Replaced damaged 16A anchor socket and tightened neutral connection wires.',
                'customer_confirmed': False
            }
        )

        # 7. Sample Notification
        Notification.objects.get_or_create(
            user=c2,
            title='Work Proof Ready for Review',
            defaults={
                'message': 'Vikram has submitted work photos for Booking #HB-2026-00102. Please review and confirm completion.',
                'notification_type': 'BOOKING',
                'link_url': f'/bookings/{b2.id}/'
            }
        )

        self.stdout.write(self.style.SUCCESS("HomeBuddy database successfully seeded with realistic demonstration data!"))
        self.stdout.write(self.style.SUCCESS("Admin Account: admin@homebuddy.local / Admin@123"))
        self.stdout.write(self.style.SUCCESS("Customer Account: rahul.sharma@example.com / Customer@123"))
        self.stdout.write(self.style.SUCCESS("Provider Account: suresh.cleaner@example.com / Provider@123"))
