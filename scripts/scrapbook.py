"""
Scrapbook SVG library — انتروبيا الحنين
Hand-drawn style visual elements: physics equations, orbital sketches,
ink stains, stamps, tickets, hand-drawn stars, moon phases, etc.

Each function returns an SVG string that can be embedded inline.
All elements use currentColor so they inherit the surrounding color.
"""

import random


def orbital_sketch(width=120, height=120, seed=None):
    """Hand-drawn orbital diagram — concentric ellipses with a planet."""
    if seed:
        random.seed(seed)
    angle1 = random.randint(-30, 30)
    angle2 = random.randint(-30, 30)
    return f'''<svg viewBox="0 0 120 120" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.6" stroke-linecap="round">
  <ellipse cx="60" cy="60" rx="50" ry="48" stroke-dasharray="0.5 1.5"/>
  <ellipse cx="60" cy="60" rx="40" ry="38" transform="rotate({angle1} 60 60)" stroke-dasharray="0.5 1.5"/>
  <ellipse cx="60" cy="60" rx="28" ry="26" transform="rotate({angle2} 60 60)"/>
  <circle cx="60" cy="60" r="3" fill="currentColor" stroke="none"/>
  <circle cx="60" cy="10" r="1.5" fill="currentColor" stroke="none"/>
  <circle cx="100" cy="60" r="1" fill="currentColor" stroke="none"/>
  <circle cx="40" cy="90" r="0.8" fill="currentColor" stroke="none"/>
</svg>'''


def equation_handwritten(width=180, height=60, text="E = mc²", seed=None):
    """Handwritten physics equation in a faint dashed box."""
    return f'''<svg viewBox="0 0 180 60" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.5">
  <rect x="2" y="2" width="176" height="56" stroke-dasharray="1 2" rx="2"/>
  <text x="90" y="38" text-anchor="middle" font-family="Amiri, serif" font-style="italic" font-size="22" fill="currentColor" stroke="none">{text}</text>
</svg>'''


def ink_stain(width=80, height=80, seed=None):
    """Organic ink stain / coffee ring — irregular blob."""
    if seed:
        random.seed(seed)
    points = []
    import math
    for i in range(12):
        angle = (i / 12) * 2 * math.pi
        r = 30 + random.randint(-8, 8)
        x = 40 + r * math.cos(angle)
        y = 40 + r * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
    return f'''<svg viewBox="0 0 80 80" width="{width}" height="{height}">
  <polygon points="{' '.join(points)}" fill="currentColor" opacity="0.08" stroke="none"/>
  <polygon points="{' '.join(points)}" fill="none" stroke="currentColor" stroke-width="0.4" opacity="0.3"/>
</svg>'''


def star_burst(width=40, height=40):
    """Hand-drawn 4-point star burst."""
    return f'''<svg viewBox="0 0 40 40" width="{width}" height="{height}" fill="currentColor">
  <path d="M20 0 L22 18 L40 20 L22 22 L20 40 L18 22 L0 20 L18 18 Z" opacity="0.7"/>
  <circle cx="20" cy="20" r="2" fill="currentColor"/>
</svg>'''


def moon_phases(width=160, height=24):
    """Row of moon phases."""
    phases = [
        ('full', 10, 12),
        ('gibbous-waning', 30, 12),
        ('half-waning', 50, 12),
        ('crescent-waning', 70, 12),
        ('new', 90, 12),
        ('crescent-waxing', 110, 12),
        ('half-waxing', 130, 12),
        ('gibbous-waxing', 150, 12),
    ]
    circles = ''
    for phase, cx, cy in phases:
        if phase == 'full':
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="currentColor" opacity="0.8"/>'
        elif phase == 'new':
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="currentColor" stroke-width="0.8"/>'
        elif 'half-waning' in phase:
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 1 {cx} {cy+8} Z" fill="currentColor" opacity="0.7"/>'
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="currentColor" stroke-width="0.4"/>'
        elif 'half-waxing' in phase:
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 0 {cx} {cy+8} Z" fill="currentColor" opacity="0.7"/>'
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="currentColor" stroke-width="0.4"/>'
        elif 'crescent-waning' in phase:
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 1 {cx} {cy+8} A 6 8 0 0 0 {cx} {cy-8} Z" fill="currentColor" opacity="0.7"/>'
        elif 'crescent-waxing' in phase:
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 0 {cx} {cy+8} A 6 8 0 0 1 {cx} {cy-8} Z" fill="currentColor" opacity="0.7"/>'
        elif 'gibbous-waning' in phase:
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="currentColor" opacity="0.7"/>'
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 0 {cx} {cy+8} A 6 8 0 0 1 {cx} {cy-8} Z" fill="var(--bg)" stroke="none"/>'
        elif 'gibbous-waxing' in phase:
            circles += f'<circle cx="{cx}" cy="{cy}" r="8" fill="currentColor" opacity="0.7"/>'
            circles += f'<path d="M {cx} {cy-8} A 8 8 0 0 1 {cx} {cy+8} A 6 8 0 0 0 {cx} {cy-8} Z" fill="var(--bg)" stroke="none"/>'
    return f'''<svg viewBox="0 0 160 24" width="{width}" height="{height}">{circles}</svg>'''


def stamp_postal(width=80, height=100, label="انتروبيا"):
    """Vintage postage stamp with perforated edges."""
    return f'''<svg viewBox="0 0 80 100" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.8">
  <rect x="6" y="6" width="68" height="88" stroke-dasharray="2 1.5" rx="1"/>
  <rect x="10" y="10" width="60" height="80" stroke-width="0.5" rx="0.5"/>
  <text x="40" y="44" text-anchor="middle" font-family="Reem Kufi, serif" font-size="9" fill="currentColor" stroke="none">{label}</text>
  <text x="40" y="58" text-anchor="middle" font-family="Amiri, serif" font-size="6" fill="currentColor" stroke="none" font-style="italic">٢٠٢٦</text>
  <line x1="20" y1="68" x2="60" y2="68" stroke-width="0.3"/>
  <text x="40" y="78" text-anchor="middle" font-family="IBM Plex Sans Arabic, sans-serif" font-size="5" fill="currentColor" stroke="none">YEMEN</text>
</svg>'''


def atom_sketch(width=100, height=100):
    """Hand-drawn atom with nucleus and 3 electron orbits."""
    return f'''<svg viewBox="0 0 100 100" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.6" stroke-linecap="round">
  <ellipse cx="50" cy="50" rx="44" ry="16" transform="rotate(0 50 50)" stroke-dasharray="0.5 1"/>
  <ellipse cx="50" cy="50" rx="44" ry="16" transform="rotate(60 50 50)" stroke-dasharray="0.5 1"/>
  <ellipse cx="50" cy="50" rx="44" ry="16" transform="rotate(120 50 50)" stroke-dasharray="0.5 1"/>
  <circle cx="50" cy="50" r="4" fill="currentColor" stroke="none"/>
  <circle cx="94" cy="50" r="1.5" fill="currentColor" stroke="none"/>
  <circle cx="28" cy="12" r="1.5" fill="currentColor" stroke="none"/>
  <circle cx="28" cy="88" r="1.5" fill="currentColor" stroke="none"/>
</svg>'''


def wave_pattern(width=200, height=30, amplitude=8):
    """Hand-drawn wave/sine pattern."""
    import math
    points = []
    for x in range(0, 201, 4):
        y = 15 + amplitude * math.sin(x / 16)
        points.append(f"{x},{y:.1f}")
    return f'''<svg viewBox="0 0 200 30" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.7" stroke-linecap="round">
  <polyline points="{' '.join(points)}" opacity="0.6"/>
</svg>'''


def ticket_stub(width=140, height=50, text="خط ٤٤"):
    """Vintage ticket stub with perforated edge."""
    return f'''<svg viewBox="0 0 140 50" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.7">
  <rect x="2" y="4" width="100" height="42" rx="2"/>
  <rect x="104" y="4" width="34" height="42" rx="2" stroke-dasharray="1 1.5"/>
  <line x1="100" y1="4" x2="100" y2="46" stroke-dasharray="1 1.5" stroke-width="0.5"/>
  <text x="52" y="22" text-anchor="middle" font-family="Reem Kufi, serif" font-size="11" fill="currentColor" stroke="none" font-weight="500">{text}</text>
  <text x="52" y="36" text-anchor="middle" font-family="Amiri, serif" font-size="7" fill="currentColor" stroke="none" font-style="italic">انتروبيا الحنين</text>
  <text x="121" y="28" text-anchor="middle" font-family="IBM Plex Sans Arabic, sans-serif" font-size="9" fill="currentColor" stroke="none" font-weight="600">٤٤</text>
</svg>'''


def hand_drawn_arrow(width=60, height=20, direction='down'):
    """Hand-drawn curved arrow."""
    if direction == 'down':
        path = "M 10 2 Q 30 8 30 18 M 25 14 L 30 18 L 35 14"
    elif direction == 'up':
        path = "M 10 18 Q 30 12 30 2 M 25 6 L 30 2 L 35 6"
    elif direction == 'right':
        path = "M 2 10 Q 8 4 18 4 M 14 9 L 18 4 L 14 0"
    else:  # left
        path = "M 58 10 Q 52 4 42 4 M 46 9 L 42 4 L 46 0"
    return f'''<svg viewBox="0 0 60 20" width="{width}" height="{height}" fill="none" stroke="currentColor" stroke-width="0.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="{path}" opacity="0.7"/>
</svg>'''


def constellation(width=160, height=80, seed=None):
    """Hand-drawn constellation — connected stars."""
    if seed:
        random.seed(seed)
    stars = [(20, 20), (50, 14), (78, 30), (110, 22), (140, 38), (90, 56), (60, 60), (130, 66)]
    connections = [(0,1),(1,2),(2,3),(3,4),(2,5),(5,6),(5,7)]
    lines = ''
    for a, b in connections:
        x1, y1 = stars[a]
        x2, y2 = stars[b]
        lines += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke-width="0.3" opacity="0.5"/>'
    dots = ''
    for x, y in stars:
        dots += f'<circle cx="{x}" cy="{y}" r="1.5" fill="currentColor" opacity="0.8"/>'
    return f'''<svg viewBox="0 0 160 80" width="{width}" height="{height}" fill="none" stroke="currentColor">
  {lines}{dots}
</svg>'''


def paper_texture_overlay(opacity=0.04):
    """Returns CSS for paper texture background overlay (paper grain)."""
    return f'''background-image:
  radial-gradient(circle at 25% 30%, rgba(28,26,23,{opacity}) 0.5px, transparent 1px),
  radial-gradient(circle at 75% 70%, rgba(28,26,23,{opacity*0.7}) 0.5px, transparent 1px),
  radial-gradient(circle at 50% 50%, rgba(28,26,23,{opacity*0.5}) 0.5px, transparent 1px);
background-size: 3mm 3mm, 5mm 5mm, 7mm 7mm;'''


# ============================================================
# Collection of scrapbook elements to scatter through the book
# ============================================================
SCRAPBOOK_COLLECTION = [
    ('orbital', orbital_sketch),
    ('equation', equation_handwritten),
    ('ink_stain', ink_stain),
    ('star_burst', star_burst),
    ('moon_phases', moon_phases),
    ('stamp', stamp_postal),
    ('atom', atom_sketch),
    ('wave', wave_pattern),
    ('ticket', ticket_stub),
    ('arrow', hand_drawn_arrow),
    ('constellation', constellation),
]

# Specific equations relevant to the novel
PHYSICS_EQUATIONS = [
    "E = mc²",                    # Einstein — energy/mass
    "F = ma",                      # Newton's 2nd law
    "ΔS ≥ 0",                      # Entropy (the title!)
    "S = k·log(W)",                # Boltzmann entropy
    "E = hν",                      # Planck
    "ΔE = Δmc²",                   # Mass-energy equivalence
    "ψ(x,t)",                      # Wave function
    "∇·E = ρ/ε₀",                  # Maxwell
    "T = 2π√(L/g)",                # Pendulum
    "F = G·m₁m₂/r²",              # Gravitation (father is physics teacher!)
]


def get_random_scrapbook(idx: int):
    """Get a deterministic scrapbook element based on index."""
    rng = random.Random(idx * 17 + 7)
    element_name = rng.choice([n for n, _ in SCRAPBOOK_COLLECTION])
    
    if element_name == 'equation':
        eq = rng.choice(PHYSICS_EQUATIONS)
        return ('equation', equation_handwritten(text=eq))
    elif element_name == 'orbital':
        return ('orbital', orbital_sketch(seed=idx))
    elif element_name == 'ink_stain':
        return ('ink_stain', ink_stain(seed=idx))
    elif element_name == 'star_burst':
        return ('star_burst', star_burst())
    elif element_name == 'moon_phases':
        return ('moon_phases', moon_phases())
    elif element_name == 'stamp':
        labels = ['انتروبيا', 'حنين', 'خط ٤٤', 'كون', 'ذاكرة', 'طاقة']
        return ('stamp', stamp_postal(label=rng.choice(labels)))
    elif element_name == 'atom':
        return ('atom', atom_sketch())
    elif element_name == 'wave':
        return ('wave', wave_pattern(amplitude=rng.randint(5, 10)))
    elif element_name == 'ticket':
        labels = ['خط ٤٤', 'خط ١٢', 'خط ١٩', 'خط ٣', 'خط ١', 'خط ٠']
        return ('ticket', ticket_stub(text=rng.choice(labels)))
    elif element_name == 'arrow':
        return ('arrow', hand_drawn_arrow(direction=rng.choice(['down','up','right','left'])))
    elif element_name == 'constellation':
        return ('constellation', constellation(seed=idx))
    return ('star_burst', star_burst())


# Test
if __name__ == '__main__':
    for i in range(8):
        name, svg = get_random_scrapbook(i)
        print(f'{i}: {name} ({len(svg)} chars)')
