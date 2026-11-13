export const categories = [
  { id: 'cleaning', name: 'Deep Cleaning', icon: 'Sparkles', count: 12 },
  { id: 'electrical', name: 'Electrician', icon: 'Zap', count: 8 },
  { id: 'plumbing', name: 'Plumber', icon: 'Wrench', count: 9 },
  { id: 'painting', name: 'Painting', icon: 'Paintbrush', count: 6 },
  { id: 'carpentry', name: 'Carpenter', icon: 'Hammer', count: 5 },
  { id: 'cooking', name: 'Cook & Chef', icon: 'Utensils', count: 4 },
  { id: 'appliance', name: 'Appliance Repair', icon: 'Tv', count: 7 },
];

export const featuredPackages = [
  {
    id: 1,
    category: 'cleaning',
    name: '2 BHK (Vacant Home) Deep Cleaning',
    sqft: 'upto 800 sq.feet',
    duration: '4-5 Hours',
    price: 5999,
    image: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80',
    description: 'Mechanized scrubbing, kitchen degreasing, bathroom descaling, balcony wiping, and dry vacuuming.',
    tag: 'Popular Package'
  },
  {
    id: 2,
    category: 'cleaning',
    name: '3 BHK (Vacant Home) Deep Cleaning',
    sqft: 'upto 1200 sq.feet',
    duration: '6-7 Hours',
    price: 6999,
    image: 'https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=600&q=80',
    description: 'Complete home sanitation: 3 bathrooms, full kitchen exhaust, windows, tile buffing, and deodorization.',
    tag: 'Best Value'
  },
  {
    id: 3,
    category: 'cleaning',
    name: '4 BHK (Vacant Home) Large Estate Clean',
    sqft: 'upto 2000 sq.feet',
    duration: '7-8 Hours',
    price: 7999,
    image: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=600&q=80',
    description: 'Deep mechanized cleaning for duplexes and large flats: mechanized floor polishing and deep balcony scrubbing.',
    tag: 'Large Homes'
  },
  {
    id: 4,
    category: 'cleaning',
    name: 'Mattress & Sofa Shampooing Service',
    sqft: '5-Seater + King Bed',
    duration: '2 Hours',
    price: 349,
    image: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=600&q=80',
    description: 'Injection-extraction shampooing machine removes deep dust mites, sweat stains, and odor.',
    tag: 'Starts at ₹349'
  },
  {
    id: 5,
    category: 'cleaning',
    name: 'Terrace & Balcony Jet Wash Cleaning',
    sqft: 'Upto 400 sq.ft',
    duration: '2-3 Hours',
    price: 1999,
    image: 'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80',
    description: 'High-pressure water jet washing to remove moss, bird droppings, and stubborn mud stains.',
    tag: 'Starts at ₹1,999'
  },
  {
    id: 6,
    category: 'electrical',
    name: 'Emergency MCB & Short Circuit Repair',
    sqft: 'Full Household',
    duration: '45 Mins',
    price: 299,
    image: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=600&q=80',
    description: 'Rapid diagnostic inspection with multimeter, burned switch replacement, and earthing test.',
    tag: 'Express 45-Min'
  }
];

export const commercialServices = [
  { name: 'Restaurant Deep Cleaning', desc: 'Commercial kitchen chimneys, grease traps & dining hall hygiene.', img: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=400&q=80' },
  { name: 'Corporate Office Cleaning', desc: 'Workstation dust extraction, carpet shampooing & conference rooms.', img: 'https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=400&q=80' },
  { name: 'Shop / Showroom Cleaning', desc: 'Glass facades, high ceilings, display racks & marble floor polishing.', img: 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=400&q=80' },
  { name: 'Post-Construction Interior Clean', desc: 'Removing cement splatter, wall putty residue & paint stains.', img: 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=400&q=80' },
];

export const verifiedTechnicians = [
  {
    id: 1,
    name: 'Suresh Jadhav',
    business: 'Suresh Safaiwala & Deep Cleaners',
    trade: 'Full House Deep Cleaning',
    rating: 4.9,
    reviews: 38,
    jobs: 64,
    verified: true,
    city: 'Pune (Kothrud, Baner, Wakad)'
  },
  {
    id: 2,
    name: 'Vikram Shinde',
    business: 'Vikram Certified Electrical Services',
    trade: 'Licensed Electrician',
    rating: 4.85,
    reviews: 24,
    jobs: 42,
    verified: true,
    city: 'Pune (Deccan, Kothrud, Aundh)'
  },
  {
    id: 3,
    name: 'Mahesh More',
    business: 'Mahesh Rapid Plumbing Care',
    trade: 'Sanitary & Drain Plumber',
    rating: 5.0,
    reviews: 18,
    jobs: 35,
    verified: true,
    city: 'Pune (Viman Nagar, Kharadi, Kalyani Nagar)'
  }
];
