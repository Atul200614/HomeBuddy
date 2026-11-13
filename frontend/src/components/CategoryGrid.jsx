import React from 'react';
import { categories } from '../data/mockData';

export default function CategoryGrid({ selectedCategory, onSelectCategory }) {
  const getIcon = (catId) => {
    switch (catId) {
      case 'cleaning': return '🧹';
      case 'electrical': return '⚡';
      case 'plumbing': return '🔧';
      case 'painting': return '🎨';
      case 'carpentry': return '🔨';
      case 'cooking': return '🍳';
      case 'appliance': return '❄️';
      default: return '🛠️';
    }
  };

  return (
    <div className="container">
      <div className="hb-section-head">
        <div>
          <h2>Your Space, Our Expertise</h2>
          <p style={{ color: '#64748B', fontSize: '0.9rem' }}>Choose your category to explore transparent, upfront pricing.</p>
        </div>
      </div>

      <div className="hb-cat-grid">
        {categories.map((c) => (
          <div 
            key={c.id} 
            className={`hb-cat-box ${selectedCategory === c.id ? 'active' : ''}`}
            onClick={() => onSelectCategory(c.id === selectedCategory ? null : c.id)}
          >
            <div className="hb-cat-ico-wrap">
              {getIcon(c.id)}
            </div>
            <div style={{ fontWeight: 800, fontSize: '0.95rem' }}>{c.name}</div>
            <div style={{ fontSize: '0.75rem', color: '#94A3B8' }}>{c.count} Services</div>
          </div>
        ))}
      </div>
    </div>
  );
}
