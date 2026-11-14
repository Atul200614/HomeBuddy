import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.customers.models import CustomerProfile, Address
from apps.professionals.models import ProviderProfile, ProviderSkill, VerificationDocument
from apps.services.models import Category, Service, ProviderService
from apps.bookings.models import Booking, BookingStatusHistory, WorkProof, LocationUpdate
from apps.payments.models import Payment, EarningsLedger, Invoice
from apps.reviews.models import Review
from apps.complaints.models import Complaint
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = "Seed database with realistic HomeBuddy demonstration data (All 6 categories, 60 services, 6 providers in Pune)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting HomeBuddy database seed..."))

        # ------------------------------------------------------------------
        # 1. Platform Admin
        # ------------------------------------------------------------------
        admin_user, _ = User.objects.get_or_create(
            email='admin@homebuddy.local',
            defaults={
                'username': 'admin',
                'first_name': 'Atul',
                'last_name': 'Patel',
                'phone': '9876543210',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True
            }
        )
        admin_user.set_password('Admin@123')
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()

        # ------------------------------------------------------------------
        # 2. Customers
        # ------------------------------------------------------------------
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
                'latitude': Decimal('18.507400'),
                'longitude': Decimal('73.807700'),
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
                'latitude': Decimal('18.559000'),
                'longitude': Decimal('73.786800'),
                'is_default': True
            }
        )

        # ------------------------------------------------------------------
        # 3. Service Categories (All 6 Categories)
        # ------------------------------------------------------------------
        cat_clean, _ = Category.objects.get_or_create(
            slug='cleaning',
            defaults={'name': 'Deep Cleaning', 'icon_name': 'bi-droplet-half', 'display_order': 1,
                      'description': 'Mechanized home sanitization, kitchen degreasing, bathroom descaling & floor buffing.'}
        )
        cat_electric, _ = Category.objects.get_or_create(
            slug='electrical',
            defaults={'name': 'Electrician', 'icon_name': 'bi-lightning-charge', 'display_order': 2,
                      'description': 'Certified wiremen for switches, fans, wiring shorts, MCB tripping & appliance repairs.'}
        )
        cat_plumb, _ = Category.objects.get_or_create(
            slug='plumbing',
            defaults={'name': 'Plumber', 'icon_name': 'bi-wrench', 'display_order': 3,
                      'description': 'Leak fix, pipe joints, bathroom sanitary fittings, drain clearing & water tanks.'}
        )
        cat_carpenter, _ = Category.objects.get_or_create(
            slug='carpentry',
            defaults={'name': 'Carpenter', 'icon_name': 'bi-hammer', 'display_order': 4,
                      'description': 'Modular furniture assembly, door locks, hinges, bed repairs & custom woodwork.'}
        )
        cat_paint, _ = Category.objects.get_or_create(
            slug='painting',
            defaults={'name': 'Painting', 'icon_name': 'bi-brush', 'display_order': 5,
                      'description': 'Interior plastic emulsion, exterior weather coats, designer textures & waterproofing.'}
        )
        cat_cook, _ = Category.objects.get_or_create(
            slug='cooking',
            defaults={'name': 'Cook & Chef', 'icon_name': 'bi-egg-fried', 'display_order': 6,
                      'description': 'Hygienic daily home meals, gourmet party chefs, breakfast, lunch & dinner specialists.'}
        )

        # ------------------------------------------------------------------
        # 4. Service Providers / Technicians (6 Dedicated Providers)
        # ------------------------------------------------------------------
        providers_meta = [
            {
                'email': 'suresh.cleaner@example.com',
                'first_name': 'Suresh',
                'last_name': 'Jadhav',
                'phone': '9822012345',
                'business_name': 'Suresh Safaiwala & Deep Cleaners',
                'bio': 'Over 8 years experience in residential deep cleaning, mechanized floor scrubbing, and post-interior paint cleaning.',
                'experience_years': 8,
                'avg_rating': Decimal('4.90'),
                'total_reviews': 38,
                'total_jobs_completed': 64,
                'skills': [('Kitchen Degreasing', 6), ('Mechanized Floor Buffing', 8), ('Sofa Foam Shampooing', 5)],
                'category': cat_clean,
            },
            {
                'email': 'vikram.electric@example.com',
                'first_name': 'Vikram',
                'last_name': 'Shinde',
                'phone': '9822054321',
                'business_name': 'Vikram Certified Electrical Services',
                'bio': 'Licensed wireman certified by Maharashtra Electrical Inspectorate. Specialized in MCB tripping, inverter wiring, and light fittings.',
                'experience_years': 6,
                'avg_rating': Decimal('4.85'),
                'total_reviews': 29,
                'total_jobs_completed': 52,
                'skills': [('MCB & Distribution Box Wiring', 6), ('Inverter & Battery Wiring', 5), ('Short Circuit Tracing', 6)],
                'category': cat_electric,
            },
            {
                'email': 'mahesh.plumber@example.com',
                'first_name': 'Mahesh',
                'last_name': 'More',
                'phone': '9822098765',
                'business_name': 'Mahesh Rapid Plumbing Solutions',
                'bio': 'Specialized in bathroom sanitary fixtures, drain unclogging, water tank pipeline connections, and leak sealing.',
                'experience_years': 5,
                'avg_rating': Decimal('4.95'),
                'total_reviews': 24,
                'total_jobs_completed': 47,
                'skills': [('Drain Blockage Clearing', 5), ('CPVC Pipe Leak Sealing', 5), ('Bathroom Diverter Fitting', 4)],
                'category': cat_plumb,
            },
            {
                'email': 'ramesh.carpenter@example.com',
                'first_name': 'Ramesh',
                'last_name': 'Sutar',
                'phone': '9822088888',
                'business_name': 'Ramesh Modern Carpentry Works',
                'bio': 'Master carpenter with 9 years expertise in modular wardrobe assembly, hydraulic bed fitting, and door locks.',
                'experience_years': 9,
                'avg_rating': Decimal('4.88'),
                'total_reviews': 31,
                'total_jobs_completed': 58,
                'skills': [('Modular Furniture Assembly', 9), ('Door & Lock Fitting', 8), ('Wood Polishing', 6)],
                'category': cat_carpenter,
            },
            {
                'email': 'prakash.painter@example.com',
                'first_name': 'Prakash',
                'last_name': 'Jadhav',
                'phone': '9822077777',
                'business_name': 'Prakash Premium Home Painters',
                'bio': 'Professional wall painter with 10 years experience in interior luxury finishes, damp-proof coatings, and texture designs.',
                'experience_years': 10,
                'avg_rating': Decimal('4.92'),
                'total_reviews': 42,
                'total_jobs_completed': 71,
                'skills': [('Interior Emulsion Painting', 10), ('Waterproof Damp Sealing', 7), ('Wall Texture Art', 6)],
                'category': cat_paint,
            },
            {
                'email': 'sunita.cook@example.com',
                'first_name': 'Sunita',
                'last_name': 'Deshmukh',
                'phone': '9822066666',
                'business_name': 'Sunita Swad Kitchen & Gourmet Chefs',
                'bio': 'FSSAI certified expert home chef specializing in hygienic Maharashtrian, North Indian, and wholesome party meals.',
                'experience_years': 7,
                'avg_rating': Decimal('4.96'),
                'total_reviews': 35,
                'total_jobs_completed': 60,
                'skills': [('North & South Indian Meals', 7), ('Healthy Daily Cooking', 7), ('Party & Banquet Menus', 5)],
                'category': cat_cook,
            },
        ]

        provider_profiles = {}
        for pdata in providers_meta:
            u, _ = User.objects.get_or_create(
                email=pdata['email'],
                defaults={
                    'username': pdata['email'],
                    'first_name': pdata['first_name'],
                    'last_name': pdata['last_name'],
                    'phone': pdata['phone'],
                    'role': 'PROVIDER'
                }
            )
            u.set_password('Provider@123')
            u.save()

            prof, _ = ProviderProfile.objects.get_or_create(
                user=u,
                defaults={
                    'business_name': pdata['business_name'],
                    'bio': pdata['bio'],
                    'experience_years': pdata['experience_years'],
                    'is_verified': True,
                    'verification_date': timezone.now(),
                    'avg_rating': pdata['avg_rating'],
                    'total_reviews': pdata['total_reviews'],
                    'total_jobs_completed': pdata['total_jobs_completed'],
                    'service_city': 'Pune',
                    'service_pincodes': '411038, 411045, 411057, 411014, 411004, 411007, 411029, 411052',
                    'is_available_today': True,
                }
            )
            for sname, syears in pdata['skills']:
                ProviderSkill.objects.get_or_create(provider=prof, skill_name=sname, defaults={'years_experience': syears})

            VerificationDocument.objects.get_or_create(
                provider=prof,
                document_type='AADHAAR',
                defaults={
                    'status': 'APPROVED',
                    'admin_notes': 'Aadhaar identity verified against UIDAI database.',
                    'reviewed_at': timezone.now()
                }
            )
            provider_profiles[pdata['category'].slug] = prof

        # ------------------------------------------------------------------
        # 5. Services Catalog (Exactly 10 Services per Category = 60 Total)
        # ------------------------------------------------------------------
        services_data = [
            # Deep Cleaning (10)
            (cat_clean, 'full-home-deep-cleaning', 'Full Home Deep Cleaning', Decimal('2999.00'), 240, False,
             'Complete mechanized deep cleaning for entire home including all rooms, kitchen, and washrooms.',
             'Comprehensive single-disc floor scrubbing, window track cleaning, fan and light wipe-down, bathroom descaling, and high-temperature kitchen sanitization.'),
            (cat_clean, 'kitchen-deep-cleaning', 'Kitchen Deep Cleaning', Decimal('1299.00'), 120, False,
             'Intensive degreasing of chimney, gas stovetop, tile grout, cabinets, and appliances.',
             'Eco-safe alkaline degreaser treatment for grease build-up on exhaust fans, slab counters, tiles, and cabinet exteriors/interiors.'),
            (cat_clean, 'bathroom-deep-cleaning', 'Bathroom Deep Cleaning', Decimal('699.00'), 60, True,
             'Hard water stain removal, sanitary disinfection, and mechanized tile scrubbing.',
             'Acid-free chemical descaling of taps, shower cubicles, WC sanitization, and grout scrubbing with anti-fungal wash.'),
            (cat_clean, 'sofa-cleaning', 'Sofa Cleaning', Decimal('899.00'), 90, False,
             'Deep fabric extraction, anti-bacterial foam cleaning, and dry vacuuming for sofas.',
             'Injection-extraction cleaning using German machinery to remove deep dust mites, pet hair, and food stains from upholstery.'),
            (cat_clean, 'bedroom-deep-cleaning', 'Bedroom Deep Cleaning', Decimal('999.00'), 90, False,
             'Mattress dusting, wardrobe exterior wiping, window track detailing, and floor polishing.',
             'Intensive bedroom sanitation including under-bed vacuuming, AC filter cleanup, cobweb removal, and switchboard wiping.'),
            (cat_clean, 'carpet-cleaning', 'Carpet Cleaning', Decimal('799.00'), 60, False,
             'Industrial foam shampooing and moisture extraction for residential area rugs.',
             'Deep rotary brush agitation followed by high-vacuum moisture extraction leaving rugs fresh, odor-free, and quick to dry.'),
            (cat_clean, 'floor-scrubbing', 'Floor Scrubbing', Decimal('1199.00'), 120, False,
             'Single-disc mechanized floor buffing and scrubbing for marble and vitrified tiles.',
             'Heavy-duty scrubber removes stubborn grime, grout stains, and dull film, restoring floor gloss and cleanliness.'),
            (cat_clean, 'move-in-move-out-cleaning', 'Move-in/Move-out Cleaning', Decimal('3499.00'), 300, False,
             'Turnkey deep sanitization, vacuuming, and disinfection for vacant properties.',
             'Full empty-house top-to-bottom clean ensuring all shelves, lofts, bathrooms, balconies, and fixtures are spotless before moving in or handing over.'),
            (cat_clean, 'balcony-cleaning', 'Balcony Cleaning', Decimal('499.00'), 45, False,
             'High pressure floor jet wash, railing rust and pigeon waste sanitization.',
             'Jet spray pressure wash of floor tiles, glass cleaning, plant pot area disinfection, and railing cleanup.'),
            (cat_clean, 'complete-apartment-cleaning', 'Complete Apartment Cleaning', Decimal('3999.00'), 360, False,
             'End-to-end deep cleaning and chemical sanitation for large 3-4 BHK flats.',
             'Full team deployment covering 3+ washrooms, utility terraces, deep carpet and upholstery vacuuming, and window tracks.'),

            # Electrician (10)
            (cat_electric, 'fan-installation', 'Fan Installation', Decimal('199.00'), 30, True,
             'Safe mounting and regulator wiring for ceiling and exhaust fans.',
             'Anchor hook inspection, motor assembly, down-rod cabling, blade balancing, and wall regulator connection.'),
            (cat_electric, 'light-installation', 'Light Installation', Decimal('149.00'), 30, False,
             'Installation of tube lights, spotlight panels, LED strip drivers, and fancy lamps.',
             'Precision drilling, ceiling anchor fixing, driver wiring, and voltage test for all lighting types.'),
            (cat_electric, 'switch-and-socket-repair', 'Switch and Socket Repair', Decimal('129.00'), 30, True,
             'Replacement of burned modular switches, 16A power points, and loose wiring.',
             'Replacing faulty switches, repairing earthing loose connections, and replacing damaged gang boxes.'),
            (cat_electric, 'wiring-repair', 'Wiring Repair', Decimal('499.00'), 60, True,
             'Multimeter short-circuit troubleshooting and wire replacement with safe conduits.',
             'Insulation testing, identification of burned neutral wires, rewiring concealed conduits, and phase load alignment.'),
            (cat_electric, 'mcb-and-fuse-repair', 'MCB and Fuse Repair', Decimal('299.00'), 45, True,
             'Diagnosis of frequent tripping and distribution box MCB / RCCB replacement.',
             'Distribution panel thermal inspection, replacement of faulty single/double pole MCB or earth leakage circuit breaker.'),
            (cat_electric, 'inverter-installation', 'Inverter Installation', Decimal('799.00'), 90, True,
             'Battery bank setup, inverter installation, and whole-home power backup wiring.',
             'Acid level check, heavy gauge battery cable crimping, main board changeover switch wiring, and load testing.'),
            (cat_electric, 'electrical-appliance-repair', 'Electrical Appliance Repair', Decimal('399.00'), 60, False,
             'Diagnostics and element/board repair for geysers, irons, microwave sockets.',
             'Thermostat checking, heating element replacement, and high-amp socket wiring for water heaters and kitchen appliances.'),
            (cat_electric, 'doorbell-installation', 'Doorbell Installation', Decimal('149.00'), 30, False,
             'Wired or wireless smart video chime setup and transformer connection.',
             'Wiring buzzer points or mounting wifi video chime base with clean exterior conduit concealing.'),
            (cat_electric, 'electrical-inspection', 'Electrical Inspection', Decimal('349.00'), 45, False,
             'Full premises earthing check, load distribution review, and safety audit.',
             'Earth pit resistance test, distribution box balancing, appliance amperage rating verification, and fire safety check.'),
            (cat_electric, 'emergency-electrical-repair', 'Emergency Electrical Repair', Decimal('599.00'), 45, True,
             'Express 30-minute priority dispatch for power blackouts and sparking sockets.',
             'Rapid response electrician equipped with multi-test tools and essential replacement breakers for urgent restoration.'),

            # Plumber (10)
            (cat_plumb, 'tap-repair', 'Tap Repair', Decimal('149.00'), 30, True,
             'Fixing dripping mixer taps, spindle replacement, and aerator scaling cleanup.',
             'Replacing worn ceramic cartridges, washers, Teflon sealing, and restoring clean laminar water flow.'),
            (cat_plumb, 'pipe-leakage-repair', 'Pipe Leakage Repair', Decimal('299.00'), 45, True,
             'Under-sink and wall pipe joint leak repair with CPVC solvent and teflon.',
             'Concealed pipe joint diagnosis, replacing cracked PVC/CPVC pipes, solvent welding, and pressure testing.'),
            (cat_plumb, 'bathroom-plumbing', 'Bathroom Plumbing', Decimal('499.00'), 60, True,
             'Complete bathroom fittings, health faucets, diverters, and overhead showers.',
             'Wall mixer servicing, hot/cold line alignment, jet spray replacement, and chrome fixture mounting.'),
            (cat_plumb, 'kitchen-sink-repair', 'Kitchen Sink Repair', Decimal('249.00'), 45, False,
             'Drain coupling replacement, trap clearing, and sink sealing with silicone.',
             'Unclogging bottle traps, replacing flexible waste couplings, and resealing sink perimeter against countertop leakages.'),
            (cat_plumb, 'water-tank-cleaning', 'Water Tank Cleaning', Decimal('999.00'), 120, False,
             'High-pressure desilting, sludge removal, and UV disinfection of overhead tanks.',
             'Submersible pump dewatering, high pressure rotary jet cleaning, anti-bacterial sludge removal, and potassium permanganate treatment.'),
            (cat_plumb, 'toilet-repair', 'Toilet Repair', Decimal('349.00'), 45, True,
             'Cistern siphon mechanism overhaul, inlet valve replacement, and seat fitting.',
             'Fixing continuous tank running water, adjusting flush float valves, replacing silicone wax rings, and seat cover installation.'),
            (cat_plumb, 'drain-blockage-removal', 'Drain Blockage Removal', Decimal('399.00'), 60, True,
             'Heavy-duty snake spring drain rod clearing for choked bathroom waste pipes.',
             'Mechanical wire rodding through nahani traps and main gully traps to dislodge hair, soap residue, and debris.'),
            (cat_plumb, 'shower-installation', 'Shower Installation', Decimal('249.00'), 30, False,
             'Concealed or exposed shower head mounting with pressure regulator.',
             'Rain shower arm extension fitting, Teflon threading, ball joint swivel adjustment, and flow testing.'),
            (cat_plumb, 'water-motor-repair', 'Water Motor Repair', Decimal('599.00'), 90, True,
             'Pump priming, capacitor replacement, and automatic float switch wiring.',
             'Centrifugal monoblock pump impeller clearing, capacitor swapping, mechanical seal leak repair, and water overhead sensor check.'),
            (cat_plumb, 'complete-plumbing-inspection', 'Complete Plumbing Inspection', Decimal('349.00'), 45, False,
             'Full house pipeline pressure check, seepage detection, and valve servicing.',
             'Inspection of main gate valves, ball valves, hidden ceiling dampness origins, pressure checking, and water hardness inspection.'),

            # Carpenter (10)
            (cat_carpenter, 'furniture-assembly', 'Furniture Assembly', Decimal('499.00'), 60, False,
             'Precision assembly of flat-pack beds, wardrobes, study desks, and TV units.',
             'Expert assembly for IKEA, Pepperfry, UrbanLadder knock-down furniture with cam locks, dowels, and level adjustments.'),
            (cat_carpenter, 'door-repair', 'Door Repair', Decimal('299.00'), 45, True,
             'Planing stuck doors, latch realignment, and hinge lubrication or replacement.',
             'Electric planer trimming for monsoon-swollen wood, tightening loose door hinges, and mortise strike plate adjustments.'),
            (cat_carpenter, 'cupboard-repair', 'Cupboard Repair', Decimal('399.00'), 60, False,
             'Telescopic channel alignment, soft-close hinge fitting, and shelf leveling.',
             'Replacing sagging wardrobe shelves, fixing loose cabinet magnetic catchers, and swapping rusted hinges.'),
            (cat_carpenter, 'bed-repair', 'Bed Repair', Decimal('449.00'), 60, False,
             'Hydraulic lift mechanism repair, plywood plank replacement, and frame reinforcement.',
             'Replacing gas lift pistons, reinforcing wooden slats, squeak elimination, and headboard secure mounting.'),
            (cat_carpenter, 'drawer-repair', 'Drawer Repair', Decimal('199.00'), 30, False,
             'Smooth ball-bearing channel replacement and drawer knob/handle fitting.',
             'Re-aligning jammed drawer boxes, upgrading to heavy-duty soft close slides, and drilling handle hardware.'),
            (cat_carpenter, 'wooden-furniture-polishing', 'Wooden Furniture Polishing', Decimal('899.00'), 120, False,
             'Melamine, PU, or natural teak wood touch-up polishing and scratch buffing.',
             'Fine sanding of surface scratches, wood filler application, staining, and protective lacquer buffing.'),
            (cat_carpenter, 'shelf-installation', 'Shelf Installation', Decimal('249.00'), 30, False,
             'Wall drilling, anchor fixing, and floating shelf mounting with spirit level.',
             'Accurate wall marking with laser/spirit level, solid rawlplug anchors, and heavy load bracket mounting.'),
            (cat_carpenter, 'modular-furniture-repair', 'Modular Furniture Repair', Decimal('599.00'), 90, False,
             'Kitchen cabinet door adjustments, edge banding re-gluing, and panel fixtures.',
             'PVA edge-band pressing, replacing soft-close lift-up tandem runners, and correcting misalignment in kitchen modules.'),
            (cat_carpenter, 'lock-installation', 'Lock Installation', Decimal('249.00'), 30, True,
             'Fitting cylindrical brass locks, deadbolts, and handles on main and internal doors.',
             'Hole-saw wood mortising, rim cylinder alignment, strike plate chiseling, and smooth key rotation testing.'),
            (cat_carpenter, 'custom-woodwork', 'Custom Woodwork', Decimal('999.00'), 120, False,
             'Custom wood cutting, partition fabrication, and bespoke carpentry repairs.',
             'On-site custom sizing of plywood partitions, pelmet boxes, curtain track mounts, and custom wooden frames.'),

            # Painting (10)
            (cat_paint, 'bedroom-painting', 'Bedroom Painting', Decimal('3499.00'), 360, False,
             'Two coats of washable plastic emulsion paint with primer and putty sanding.',
             'Comprehensive bedroom painting including crack filling with acrylic putty, base primer application, and dual top coats of Asian Paints Royale / Apcolite.'),
            (cat_paint, 'living-room-painting', 'Living Room Painting', Decimal('4999.00'), 480, False,
             'Premium luster/acrylic wall painting with ceiling coat and wall protection masking.',
             'Masking electrical switches and skirting, filling hairline plaster cracks, applying 2 coats of premium low-odor paint, and full cleanup.'),
            (cat_paint, 'full-home-painting', 'Full Home Painting', Decimal('14999.00'), 1440, False,
             'Complete 2/3 BHK interior makeover with damp-proof primer, putty, and paint.',
             'Turnkey residential interior painting package covering living room, all bedrooms, kitchen, passage, ceilings, and touch-up on woodwork.'),
            (cat_paint, 'wall-repainting', 'Wall Repainting', Decimal('1999.00'), 240, False,
             'Touch-up reapplication of matching paint shades over faded or soiled walls.',
             'Surface washing of grease, light sanding, spot puttying, and two roller coats of exact shade-matched emulsion.'),
            (cat_paint, 'texture-painting', 'Texture Painting', Decimal('3999.00'), 360, False,
             'Artistic designer feature wall textures with metallic or stone-finish roller effects.',
             'Specialty stucco / metallics / safari / dune patterns crafted on your living or master bedroom accent wall by certified painters.'),
            (cat_paint, 'exterior-painting', 'Exterior Painting', Decimal('8999.00'), 720, False,
             'Weather-proof silicon exterior emulsion coating for balconies and house facades.',
             'Anti-algae exterior paint application resistant to harsh sun and heavy monsoon rains with 3-5 year weather protection.'),
            (cat_paint, 'waterproof-painting', 'Waterproof Painting', Decimal('4499.00'), 360, False,
             'Anti-fungal elastomeric damp-block barrier paint for moisture-prone areas.',
             'Deep penetration epoxy-acrylic damp block primer followed by high-stretch waterproof membrane top coat on affected walls.'),
            (cat_paint, 'door-and-window-painting', 'Door and Window Painting', Decimal('1299.00'), 120, False,
             'Synthetic enamel gloss / satin paint coating for wooden and metal frames.',
             'Rust scraping on grills, wood sanding, red oxide / wood primer coat, and double high-gloss enamel finishing.'),
            (cat_paint, 'office-painting', 'Office Painting', Decimal('7999.00'), 600, False,
             'Low-VOC commercial paint application for offices and commercial cabins.',
             'Quick-drying zero-odor commercial emulsion paint allowing minimal downtime for office operations and reception areas.'),
            (cat_paint, 'touch-up-painting', 'Touch-up Painting', Decimal('999.00'), 90, False,
             'Minor patch filling, sanding, and roller touch-up on scuffed walls.',
             'Targeted patch repair for nail holes, move-in sofa scrapes, water ring stains, and minor drywall imperfections.'),

            # Cook & Chef (10)
            (cat_cook, 'daily-home-cook', 'Daily Home Cook', Decimal('3999.00'), 60, False,
             'Healthy, home-style daily meal preparation tailored to your family\'s dietary needs.',
             'Experienced cook prepares wholesome rotis, sabzi, dal, and rice customized to your taste, oil preference, and spice level.'),
            (cat_cook, 'vegetarian-cook', 'Vegetarian Cook', Decimal('3499.00'), 60, False,
             'Pure vegetarian breakfast, lunch, and dinner recipes made with fresh ingredients.',
             'Jain or pure vegetarian kitchen standards, preparing fresh paneer curries, lentils, seasonal vegetables, and warm flatbreads.'),
            (cat_cook, 'non-vegetarian-cook', 'Non-Vegetarian Cook', Decimal('4499.00'), 60, False,
             'Authentic chicken, mutton, seafood curries, and biryani specialties.',
             'Specialist in traditional regional non-veg preparations including Dum Biryani, Kolhapuri Rassa, butter chicken, and fish fry.'),
            (cat_cook, 'full-time-cook', 'Full-Time Cook', Decimal('7999.00'), 240, False,
             'Dedicated in-house chef for full-day breakfast, lunch, tea, snacks, and dinner service.',
             'Comprehensive kitchen management, grocery prep, multi-course dining, and complete kitchen tidying after each meal.'),
            (cat_cook, 'part-time-cook', 'Part-Time Cook', Decimal('2499.00'), 45, False,
             'Quick single-meal prep (rotis, sabzi, dal, rice) for busy professionals.',
             'Swift, hygienic preparation of everyday lunch or dinner so you always arrive home to fresh hot food.'),
            (cat_cook, 'breakfast-preparation', 'Breakfast Preparation', Decimal('1499.00'), 45, False,
             'Fresh south Indian dosas, idlis, parathas, poha, and health bowls every morning.',
             'Daily morning visit preparing hot filter coffee, tea, crisp dosas, stuffed parathas, or nutritious oatmeal bowls.'),
            (cat_cook, 'lunch-preparation', 'Lunch Preparation', Decimal('1999.00'), 60, False,
             'Balanced 3-course mid-day meals packed fresh for office or family dining.',
             'Fresh lunch preparation consisting of salad, cooked pulses, seasonal curry, and fluffy chapatis ready by noon.'),
            (cat_cook, 'dinner-preparation', 'Dinner Preparation', Decimal('1999.00'), 60, False,
             'Light, nutritious evening meals and fresh warm chapatis prepared on time.',
             'Nutritious, easy-to-digest dinner meals cooked fresh in the evening to wind down your busy workday.'),
            (cat_cook, 'party-chef', 'Party Chef', Decimal('1999.00'), 180, False,
             'Live party kitchen chef for hosting 10-30 guests with starters and main courses.',
             'Professional multi-cuisine chef to cook live appetisers, tikkas, main course gravies, and desserts for birthday or house parties.'),
            (cat_cook, 'special-occasion-cooking', 'Special Occasion Cooking', Decimal('2499.00'), 240, False,
             'Festive feast and traditional banquet preparation for poojas and ceremonies.',
             'Traditional festive satvik preparations including puran poli, modaks, kheer, festive dals, and traditional thalis.'),
        ]

        created_services = {}
        for cat, slug, name, price, duration, emergency, short_desc, detailed_desc in services_data:
            s, _ = Service.objects.update_or_create(
                slug=slug,
                defaults={
                    'category': cat,
                    'name': name,
                    'base_price': price,
                    'estimated_duration_minutes': duration,
                    'is_emergency_eligible': emergency,
                    'emergency_surcharge': Decimal('149.00') if emergency else Decimal('0.00'),
                    'short_description': short_desc,
                    'detailed_description': detailed_desc,
                    'is_active': True,
                    'pricing_type': 'FIXED' if price < Decimal('5000.00') else 'PACKAGE'
                }
            )
            created_services[slug] = s

            # Link offering provider
            provider = provider_profiles.get(cat.slug)
            if provider:
                ProviderService.objects.get_or_create(
                    provider=provider,
                    service=s,
                    defaults={'custom_price': price, 'is_active': True}
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(services_data)} bookable services across all 6 categories."))

        # ------------------------------------------------------------------
        # 6. Realistic Demonstration Bookings
        # ------------------------------------------------------------------
        today = datetime.date.today()

        # Booking 1: COMPLETED (Deep Cleaning) with WorkProof, Payment, Earnings, Invoice, Review
        s_clean = created_services['full-home-deep-cleaning']
        p_clean = provider_profiles['cleaning']
        b1, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00101',
            defaults={
                'customer': c1_prof,
                'provider': p_clean,
                'service': s_clean,
                'address': addr1,
                'scheduled_date': today - datetime.timedelta(days=2),
                'time_slot': '10:00 AM - 12:00 PM',
                'status': 'COMPLETED',
                'service_price': s_clean.base_price,
                'total_amount': s_clean.base_price,
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
                'amount': s_clean.base_price,
                'payment_method': 'ONLINE_RAZORPAY',
                'status': 'SUCCESS',
                'razorpay_payment_id': 'pay_demo_success_101',
                'razorpay_order_id': 'order_HB_2026_00101'
            }
        )
        EarningsLedger.objects.get_or_create(
            booking=b1,
            defaults={
                'provider': p_clean,
                'gross_amount': s_clean.base_price,
                'commission_rate': Decimal('10.00'),
                'commission_amount': (s_clean.base_price * Decimal('0.10')).quantize(Decimal('0.01')),
                'net_earnings': (s_clean.base_price * Decimal('0.90')).quantize(Decimal('0.01'))
            }
        )
        Invoice.objects.get_or_create(
            booking=b1,
            defaults={
                'invoice_number': 'INV-2026-00101',
                'subtotal': s_clean.base_price,
                'total_amount': s_clean.base_price
            }
        )
        Review.objects.get_or_create(
            booking=b1,
            defaults={
                'customer': c1_prof,
                'provider': p_clean,
                'rating': 5,
                'review_text': 'Suresh and his team were polite, on time, and performed an outstanding cleaning job. Highly recommended!',
                'is_approved': True
            }
        )

        # Booking 2: WORK_PROOF_SUBMITTED (Electrician)
        s_elec = created_services['switch-and-socket-repair']
        p_elec = provider_profiles['electrical']
        b2, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00102',
            defaults={
                'customer': c2_prof,
                'provider': p_elec,
                'service': s_elec,
                'address': addr2,
                'scheduled_date': today,
                'time_slot': '02:00 PM - 04:00 PM',
                'status': 'WORK_PROOF_SUBMITTED',
                'service_price': s_elec.base_price,
                'total_amount': s_elec.base_price,
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

        # Booking 3: EN_ROUTE with LIVE GPS LOCATION TRACKING (Mahesh Plumber)
        s_plumb = created_services['pipe-leakage-repair']
        p_plumb = provider_profiles['plumbing']
        b3, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00103',
            defaults={
                'customer': c1_prof,
                'provider': p_plumb,
                'service': s_plumb,
                'address': addr1,
                'scheduled_date': today,
                'time_slot': '04:00 PM - 06:00 PM',
                'status': 'EN_ROUTE',
                'service_price': s_plumb.base_price,
                'total_amount': s_plumb.base_price,
                'special_instructions': 'Master bathroom mixer pipe dripping under sink.'
            }
        )
        # Create live location points approaching Kothrud (18.5074, 73.8077)
        LocationUpdate.objects.get_or_create(
            booking=b3,
            provider=p_plumb,
            latitude=Decimal('18.502100'),
            longitude=Decimal('73.811500'),
            defaults={'heading': Decimal('320.00'), 'speed': Decimal('28.50')}
        )

        # Booking 4: REQUESTED (Carpenter)
        s_carp = created_services['furniture-assembly']
        p_carp = provider_profiles['carpentry']
        b4, _ = Booking.objects.get_or_create(
            booking_number='HB-2026-00104',
            defaults={
                'customer': c2_prof,
                'provider': p_carp,
                'service': s_carp,
                'address': addr2,
                'scheduled_date': today + datetime.timedelta(days=1),
                'time_slot': '10:00 AM - 12:00 PM',
                'status': 'REQUESTED',
                'service_price': s_carp.base_price,
                'total_amount': s_carp.base_price,
                'special_instructions': 'Assembly of 3-door wardrobe with mirror.'
            }
        )

        # Notification for customer
        Notification.objects.get_or_create(
            user=c1,
            title='Technician En Route',
            defaults={
                'message': f'Mahesh More is en route to your location for Booking #{b3.booking_number}. Live map tracking is active.',
                'notification_type': 'BOOKING',
                'link_url': f'/bookings/{b3.id}/'
            }
        )

        self.stdout.write(self.style.SUCCESS("HomeBuddy database successfully seeded with realistic demonstration data!"))
        self.stdout.write(self.style.SUCCESS("Admin Account: admin / admin@homebuddy.local / Admin@123"))
        self.stdout.write(self.style.SUCCESS("Customer Account: rahul.sharma@example.com / Customer@123"))
        self.stdout.write(self.style.SUCCESS("Provider Accounts (Password: Provider@123):"))
        for pdata in providers_meta:
            self.stdout.write(self.style.SUCCESS(f"  - {pdata['first_name']} {pdata['last_name']} ({pdata['category'].name}): {pdata['email']}"))
