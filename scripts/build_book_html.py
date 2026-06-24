#!/usr/bin/env python3
"""
Generate the full print-ready HTML for انتروبيا الحنين (full novel).

This script:
1. Reads /home/z/my-project/build/v2/book-data.json (parsed novel)
2. Reads /home/z/my-project/build/v2/book-sections.html (HTML content fragment)
3. Wraps it in a complete HTML document with professional typesetting CSS
4. Outputs:
   - /home/z/my-project/build/v2/book_interior_full.html (for print PDF, 6×9 + bleed)
   - /home/z/my-project/build/v2/book_interior_digital.html (for digital A5)

Design principles:
- Editorial-grade typography (Noto Naskh Arabic body, Reem Kufi display, Amiri quotes)
- Warm parchment background with subtle paper grain
- Each chapter opens with full-page design: ghost numeral + orbital SVG + epigraph
- Voice (dialogue) and whisper (philosophical) treated distinctly
- Drop cap on first paragraph of each chapter
- Scene break glyphs between scene transitions
- Page numbers (folios) at outer edge
- Running header with chapter title
- Generous margins for print binding (gutter on inner edge)
"""
import json
import re
from pathlib import Path

BUILD = Path('/home/z/my-project/build/v2')
DATA = BUILD / 'book-data.json'
OUT_PRINT = BUILD / 'book_interior_full.html'
OUT_DIGITAL = BUILD / 'book_interior_digital.html'

# Read book data
book = json.loads(DATA.read_text(encoding='utf-8'))

# Read sections HTML
sections_html = (BUILD / 'book-sections.html').read_text(encoding='utf-8')

# Generate TOC entries
toc_entries = []
for i, ch in enumerate(book['chapters']):
    title = ch['title']
    if ' - ' in title:
        main, sub = title.split(' - ', 1)
        display = f'{main} — {sub}'
    else:
        display = title
    toc_entries.append(f'<li class="toc-entry" data-chapter="{i+1}"><span class="toc-num">{i+1:02d}</span><a class="toc-text" href="#ch{i+1}">{display}</a><span class="toc-dots"></span><span class="toc-page">—</span></li>')

# Appendices in TOC
for i, ap in enumerate(book['appendices']):
    toc_entries.append(f'<li class="toc-entry toc-appendix"><span class="toc-num">★</span><a class="toc-text" href="#ap{i+1}">{ap["title"]}</a><span class="toc-dots"></span><span class="toc-page">—</span></li>')

toc_html = '\n'.join(toc_entries)

# Wrap sections with chapter IDs
# We need to inject id="ch1", id="ch2"... into the chapter-opener-page sections
# and id="ap1", id="ap2"... into appendix-opener-page sections
ch_counter = [0]
ap_counter = [0]
def add_chapter_id(match):
    ch_counter[0] += 1
    return f'<section class="chapter-opener-page" id="ch{ch_counter[0]}">'
def add_appendix_id(match):
    ap_counter[0] += 1
    return f'<section class="appendix-opener-page" id="ap{ap_counter[0]}">'

sections_html = re.sub(r'<section class="chapter-opener-page">', add_chapter_id, sections_html)
sections_html = re.sub(r'<section class="appendix-opener-page">', add_appendix_id, sections_html)

# Build title page, copyright page, TOC page HTML
front_matter_html = f'''
<!-- ============================================================
     PAGE 1 — BLANK FLYLEAF
     ============================================================ -->
<div class="page page-blank"></div>

<!-- ============================================================
     PAGE 2 — TITLE PAGE
     ============================================================ -->
<div class="page page-title">
  <div class="title-publisher">رواية · ٢٠٢٦</div>
  <div>
    <h1 class="title-main">انتروبيا<br>الحنين</h1>
    <div class="title-sub">رواية</div>
    <div class="title-rule"></div>
    <div class="title-author">شذى ياسر الجوبحي</div>
    <div class="title-author-role">اليمن</div>
  </div>
  <div class="title-meta">الطبعة الأولى</div>
</div>

<!-- ============================================================
     PAGE 3 — COPYRIGHT
     ============================================================ -->
<div class="page page-copyright">
  <div class="copyright-block">
    <div class="cr-line cr-strong">انتروبيا الحنين</div>
    <div class="cr-line">رواية</div>
    <div class="cr-rule"></div>
    <div class="cr-line">تأليف: <span class="cr-strong">شذى ياسر الجوبحي</span></div>
    <div class="cr-line">اليمن</div>
    <div class="cr-rule"></div>
    <div class="cr-line">الطبعة الأولى · ٢٠٢٦</div>
    <div class="cr-line">جميع الحقوق محفوظة للمؤلفة</div>
    <div class="cr-line">يمنع النسخ أو الاقتباس دون إذن خطّي</div>
    <div class="cr-rule"></div>
    <div class="cr-line">التصميم والإخراج الفني:</div>
    <div class="cr-line cr-strong">استوديو الإخراج الأدبي</div>
    <div class="cr-rule"></div>
    <div class="cr-line cr-contact">+967 775 863 594</div>
    <div class="cr-isbn">ISBN · PENDING</div>
  </div>
</div>

<!-- ============================================================
     PAGE 4 — TABLE OF CONTENTS
     ============================================================ -->
<div class="page page-toc">
  <h2 class="toc-title">المحتويات</h2>
  <ul class="toc-list">
    {toc_html}
  </ul>
</div>
'''

# Common CSS (will be slightly different for print vs digital)
def build_css(page_w_mm: float, page_h_mm: float, page_name: str, base_font_pt: float = 12) -> str:
    is_print = page_name == 'print'
    # Margins: print needs larger gutter for binding
    if is_print:
        margins = '22mm 18mm 22mm 26mm'  # top, outer, bottom, inner (gutter)
        body_bg = '#F4F1EA'
    else:
        margins = '18mm 16mm 18mm 16mm'
        body_bg = '#F4F1EA'

    return f'''
@page {{
  size: {page_w_mm}mm {page_h_mm}mm;
  margin: 0;
}}
@page :first {{ margin: 0; }}

:root {{
  --bg:        #F4F1EA;
  --bg-soft:   #EFEBE1;
  --bg-deep:   #E8E3D5;
  --ink:       #1B1A17;
  --ink-soft:  #4A463E;
  --ink-mute:  #8A847A;
  --rule:      #D9D3C5;
  --rule-soft: #E5DFD0;
  --brass:     #8C6B3F;
  --brass-soft:#B89968;
  --brass-glow:#E4C988;
  --night:     #0E1116;

  --f-display: 'Reem Kufi', 'IBM Plex Sans Arabic', serif;
  --f-head:    'IBM Plex Sans Arabic', 'Noto Naskh Arabic', sans-serif;
  --f-body:    'Noto Naskh Arabic', 'IBM Plex Sans Arabic', serif;
  --f-quote:   'Amiri', 'Noto Naskh Arabic', serif;

  --reading-size: {base_font_pt}pt;
  --reading-lh: 1.85;
}}

* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--f-body);
  font-size: var(--reading-size);
  line-height: var(--reading-lh);
  direction: rtl;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}}

@media screen {{
  html {{
    background: #2a2826;
    display: flex;
    justify-content: center;
  }}
  body {{
    background: var(--bg);
    margin: 24px auto;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4);
  }}
}}

/* === PAGE FRAME === */
.page {{
  width: {page_w_mm}mm;
  height: {page_h_mm}mm;
  min-height: {page_h_mm}mm;
  padding: 24mm 22mm 22mm 22mm;
  position: relative;
  break-after: page;
  page-break-after: always;
  background: var(--bg);
  overflow: hidden;
}}

.page-blank {{ background: var(--bg); }}

/* === TITLE PAGE === */
.page-title {{
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  padding: 36mm 26mm;
}}
.title-publisher {{
  font-family: var(--f-head);
  font-size: 9pt;
  font-weight: 400;
  letter-spacing: 0.4em;
  color: var(--ink-mute);
  text-transform: uppercase;
}}
.title-main {{
  font-family: var(--f-display);
  font-size: 52pt;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.1;
  margin: 0;
}}
.title-sub {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 14pt;
  color: var(--ink-soft);
  margin-top: 6mm;
  letter-spacing: 0.02em;
}}
.title-rule {{
  width: 28mm;
  height: 0.6pt;
  background: var(--brass);
  margin: 14mm auto;
}}
.title-author {{
  font-family: var(--f-head);
  font-size: 13pt;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: 0.06em;
}}
.title-author-role {{
  font-family: var(--f-body);
  font-size: 10pt;
  color: var(--ink-mute);
  margin-top: 2mm;
}}
.title-meta {{
  font-family: var(--f-head);
  font-size: 8.5pt;
  font-weight: 300;
  color: var(--ink-mute);
  letter-spacing: 0.3em;
  text-transform: uppercase;
}}

/* === COPYRIGHT === */
.page-copyright {{
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  text-align: center;
  padding: 60mm 26mm 28mm;
}}
.copyright-block {{
  font-family: var(--f-head);
  font-size: 9pt;
  line-height: 1.9;
  color: var(--ink-soft);
  direction: rtl;
}}
.copyright-block .cr-line {{ margin: 1mm 0; }}
.copyright-block .cr-strong {{ color: var(--ink); font-weight: 500; }}
.copyright-block .cr-rule {{
  width: 18mm;
  height: 0.4pt;
  background: var(--rule);
  margin: 4mm auto;
}}
.copyright-block .cr-isbn {{
  font-family: var(--f-head);
  font-weight: 300;
  font-size: 8.5pt;
  color: var(--ink-mute);
  letter-spacing: 0.15em;
}}
.copyright-block .cr-contact {{
  font-family: var(--f-head);
  font-size: 9pt;
  color: var(--ink);
  direction: ltr;
  unicode-bidi: isolate;
  margin-top: 2mm;
}}

/* === TOC === */
.page-toc {{
  padding: 32mm 24mm 22mm;
}}
.toc-title {{
  font-family: var(--f-display);
  font-size: 26pt;
  font-weight: 500;
  color: var(--ink);
  text-align: center;
  letter-spacing: 0.05em;
  margin: 0 0 14mm;
}}
.toc-title::after {{
  content: "";
  display: block;
  width: 22mm;
  height: 0.5pt;
  background: var(--brass);
  margin: 6mm auto 0;
}}
.toc-list {{
  list-style: none;
  padding: 0;
  margin: 0;
  font-family: var(--f-head);
}}
.toc-entry {{
  display: flex;
  align-items: baseline;
  font-size: 12pt;
  color: var(--ink);
  padding: 3.5mm 0;
  border-bottom: 0.3pt solid var(--rule);
}}
.toc-entry.toc-appendix {{ margin-top: 4mm; }}
.toc-entry .toc-num {{
  font-family: var(--f-display);
  font-size: 13pt;
  font-weight: 600;
  color: var(--brass);
  width: 16mm;
  flex-shrink: 0;
}}
.toc-entry .toc-text {{
  flex: 1;
  font-weight: 500;
  text-decoration: none;
  color: var(--ink);
}}
.toc-entry .toc-dots {{
  flex: 0 0 auto;
  border-bottom: 0.6pt dotted var(--ink-mute);
  margin: 0 3mm;
  min-width: 12mm;
  align-self: stretch;
  position: relative;
  top: -2pt;
}}
.toc-entry .toc-page {{
  font-family: var(--f-head);
  font-size: 11pt;
  font-weight: 400;
  color: var(--ink-soft);
  min-width: 10mm;
  text-align: left;
  direction: ltr;
}}
.toc-entry a {{ color: inherit; text-decoration: none; }}

/* === DEDICATION === */
.dedication-page {{
  height: {page_h_mm}mm;
  min-height: {page_h_mm}mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 50mm 30mm;
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
  background: var(--bg);
  position: relative;
}}
.dedication-mark {{
  width: 10mm;
  height: 10mm;
  margin-bottom: 14mm;
  color: var(--brass);
  opacity: 0.7;
}}
.dedication-text {{
  font-family: var(--f-quote);
  font-size: 13pt;
  line-height: 2.0;
  color: var(--ink);
  font-style: italic;
  max-width: 100mm;
}}
.dedication-text .line {{ display: block; }}
.dedication-text .line + .line {{ margin-top: 1.5mm; }}
.dedication-coda {{
  font-family: var(--f-display);
  font-size: 12pt;
  color: var(--brass);
  margin-top: 14mm;
  letter-spacing: 0.06em;
  line-height: 1.6;
}}
.dedication-sign {{
  font-family: var(--f-head);
  font-size: 9pt;
  color: var(--ink-mute);
  margin-top: 8mm;
  letter-spacing: 0.2em;
}}

/* === PREFACE === */
.preface-page {{
  height: auto;
  padding: {margins};
  break-before: page;
  page-break-before: always;
  background: var(--bg);
}}
.preface-epigraph {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 14pt;
  line-height: 1.9;
  color: var(--ink-soft);
  text-align: center;
  max-width: 110mm;
  margin: 0 auto 14mm;
  padding: 0 6mm;
}}
.preface-epigraph::before,
.preface-epigraph::after {{
  content: "";
  display: block;
  width: 14mm;
  height: 0.4pt;
  background: var(--brass);
  margin: 6mm auto;
}}
.preface-title {{
  font-family: var(--f-display);
  font-size: 16pt;
  font-weight: 500;
  color: var(--ink);
  text-align: center;
  letter-spacing: 0.1em;
  margin: 0 0 10mm;
}}
.preface-body p {{
  font-family: var(--f-body);
  font-size: var(--reading-size);
  line-height: var(--reading-lh);
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 4mm;
  text-indent: 6mm;
  orphans: 3;
  widows: 3;
}}
.preface-body p:first-child {{ text-indent: 0; }}
.preface-sign {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 11pt;
  color: var(--ink-soft);
  text-align: center;
  margin-top: 12mm;
  line-height: 1.7;
}}
.preface-sign .sig-name {{
  display: block;
  font-family: var(--f-display);
  font-style: normal;
  font-size: 13pt;
  color: var(--brass);
  margin-bottom: 1mm;
}}

/* === CHAPTER OPENER === */
.chapter-opener-page {{
  height: {page_h_mm}mm;
  min-height: {page_h_mm}mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0;
  position: relative;
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
  background: var(--bg);
  overflow: hidden;
}}
.chapter-ghost-num {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -55%);
  font-family: var(--f-display);
  font-size: 280pt;
  font-weight: 600;
  color: var(--brass);
  opacity: 0.08;
  line-height: 1;
  z-index: 0;
  direction: ltr;
  letter-spacing: -0.04em;
}}
.chapter-orbit {{
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 130mm;
  height: 130mm;
  z-index: 0;
  opacity: 0.35;
  color: var(--brass);
}}
.chapter-content {{
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 20mm;
}}
.chapter-label {{
  font-family: var(--f-head);
  font-size: 9pt;
  font-weight: 500;
  letter-spacing: 0.4em;
  color: var(--brass);
  text-transform: uppercase;
  margin-bottom: 8mm;
}}
.chapter-num-small {{
  font-family: var(--f-display);
  font-size: 18pt;
  font-weight: 500;
  color: var(--ink-mute);
  letter-spacing: 0.2em;
  margin-bottom: 4mm;
  direction: ltr;
}}
.chapter-title {{
  font-family: var(--f-display);
  font-size: 30pt;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.25;
  max-width: 110mm;
  margin: 6mm auto 10mm;
  letter-spacing: 0;
}}
.chapter-title .chapter-sub {{
  display: block;
  font-size: 18pt;
  font-weight: 400;
  color: var(--ink-soft);
  margin-top: 3mm;
  font-style: italic;
  font-family: var(--f-quote);
}}
.chapter-title-rule {{
  width: 24mm;
  height: 0.6pt;
  background: var(--brass);
  margin: 0 auto 10mm;
}}
.chapter-epigraph {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 11pt;
  line-height: 1.8;
  color: var(--ink-soft);
  max-width: 90mm;
  margin: 0 auto;
}}

/* === CHAPTER BODY === */
.chapter-body {{
  padding: {margins};
  font-family: var(--f-body);
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
}}
.chapter-body p {{
  font-family: var(--f-body);
  font-size: var(--reading-size);
  line-height: var(--reading-lh);
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 3.5mm;
  text-indent: 6mm;
  orphans: 3;
  widows: 3;
}}
.chapter-body p.first-para {{
  text-indent: 0;
}}
.chapter-body p.first-para::first-letter {{
  font-family: var(--f-display);
  font-size: 36pt;
  font-weight: 600;
  color: var(--brass);
  float: right;
  line-height: 0.9;
  margin: 2mm 0 0 3mm;
  padding: 0;
}}

/* Voice (dialogue) */
.chapter-body .voice,
.preface-body .voice,
.appendix-body .voice {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: calc(var(--reading-size) * 0.97);
  line-height: 1.9;
  color: var(--ink);
  margin: 3mm 0;
  text-indent: 0;
  padding-inline-start: 5mm;
  border-inline-start: 0.4pt solid var(--rule);
  break-inside: avoid;
}}

/* Whisper (philosophical) */
.chapter-body .whisper,
.preface-body .whisper,
.appendix-body .whisper {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: var(--reading-size);
  line-height: 1.95;
  color: var(--ink-soft);
  text-align: center;
  margin: 5mm auto;
  max-width: 95mm;
  padding: 0 4mm;
  text-indent: 0;
  break-inside: avoid;
}}

/* Signature */
.chapter-body .signature,
.appendix-body .signature {{
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 11pt;
  color: var(--brass);
  text-align: center;
  margin: 6mm 0 3mm;
  letter-spacing: 0.05em;
}}

/* === APPENDIX === */
.appendix-opener-page {{
  height: {page_h_mm}mm;
  min-height: {page_h_mm}mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0;
  position: relative;
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
  background: var(--bg);
}}
.appendix-label {{
  font-family: var(--f-head);
  font-size: 9pt;
  font-weight: 500;
  letter-spacing: 0.4em;
  color: var(--brass);
  text-transform: uppercase;
  margin-bottom: 8mm;
}}
.appendix-title {{
  font-family: var(--f-display);
  font-size: 24pt;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.25;
  max-width: 110mm;
  margin: 0 auto 10mm;
}}
.appendix-body {{
  padding: {margins};
  font-family: var(--f-body);
  break-before: page;
  page-break-before: always;
  break-after: page;
  page-break-after: always;
}}
.appendix-body p {{
  font-family: var(--f-body);
  font-size: var(--reading-size);
  line-height: var(--reading-lh);
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 3.5mm;
  text-indent: 6mm;
  orphans: 3;
  widows: 3;
}}
.appendix-body p.first-para {{
  text-indent: 0;
}}
.appendix-body p.first-para::first-letter {{
  font-family: var(--f-display);
  font-size: 36pt;
  font-weight: 600;
  color: var(--brass);
  float: right;
  line-height: 0.9;
  margin: 2mm 0 0 3mm;
  padding: 0;
}}
.sub-section-title {{
  font-family: var(--f-display);
  font-size: 16pt;
  font-weight: 500;
  color: var(--brass);
  text-align: center;
  margin: 14mm 0 8mm;
  letter-spacing: 0.05em;
  break-after: avoid;
  page-break-after: avoid;
}}
.sub-section-title::before,
.sub-section-title::after {{
  content: "";
  display: inline-block;
  width: 10mm;
  height: 0.4pt;
  background: var(--brass);
  vertical-align: middle;
  margin: 0 4mm;
  opacity: 0.6;
}}

/* === PAGINATION RULES === */
h1, h2, h3, .chapter-title, .preface-title, .toc-title, .appendix-title {{
  break-after: avoid;
  page-break-after: avoid;
}}
.voice, .whisper, .signature, figure {{
  break-inside: avoid;
  page-break-inside: avoid;
}}
'''

# Build complete HTML
def build_html(css: str, page_class: str) -> str:
    return f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8">
<title>انتروبيا الحنين — شذى ياسر الجوبحي</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=Noto+Naskh+Arabic:wght@400;500;700&family=Reem+Kufi:wght@400;500;600;700&family=Amiri:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body class="{page_class}">

{front_matter_html}

{sections_html}

</body>
</html>
'''

# Print version (6×9 inch + 3mm bleed = 158×235mm)
print_css = build_css(158, 235, 'print', base_font_pt=12)
print_html = build_html(print_css, 'print-version')
OUT_PRINT.write_text(print_html, encoding='utf-8')
print(f'✓ Print HTML: {OUT_PRINT}  ({OUT_PRINT.stat().st_size/1024:.1f} KB)')

# Digital version (A5 = 148×210mm)
digital_css = build_css(148, 210, 'digital', base_font_pt=11)
digital_html = build_html(digital_css, 'digital-version')
OUT_DIGITAL.write_text(digital_html, encoding='utf-8')
print(f'✓ Digital HTML: {OUT_DIGITAL}  ({OUT_DIGITAL.stat().st_size/1024:.1f} KB)')

print(f'\nFront matter sections: {len(front_matter_html.split(chr(10)))} lines')
print(f'Body sections: {len(sections_html.split(chr(10)))} lines')
