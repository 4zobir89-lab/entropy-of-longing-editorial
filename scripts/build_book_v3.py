#!/usr/bin/env python3
"""
Build the v3 print HTML — Classic Literary Book Design.

Key improvements over v2:
- Smaller page size: A5 (148×210mm) + 3mm bleed = 154×216mm
- Larger font: 13pt body, line-height 2.0
- Dialogue splitting: each speaker in own paragraph
- Qibas after each chapter (dedicated pages)
- Paged.js for proper running headers + page numbers
- NO break-after: page on content (only break-before on chapter starts)
- Classic literary typography (Noto Naskh + Reem Kufi + Amiri)
- Generates 100+ pages naturally
"""
import json
from pathlib import Path

BUILD = Path('/home/z/my-project/build/v3')
DATA = BUILD / 'book-data-v3.json'
OUT_PRINT = BUILD / 'book_interior_v3.html'

book = json.loads(DATA.read_text(encoding='utf-8'))

# === Build HTML body ===
body_parts = []

# --- Front matter ---
# Page 1: Blank flyleaf
# Page 1: Half-title (replaces blank flyleaf)
body_parts.append('<section class="half-title-page"><div class="half-title">انتروبيا الحنين</div><div class="half-title-sub">رواية</div></section>')

# Page 2: Title page
body_parts.append('''<section class="title-page">
  <div class="title-publisher">رواية · ٢٠٢٦</div>
  <div class="title-main-block">
    <h1 class="title-main">انتروبيا الحنين</h1>
    <div class="title-sub">رواية</div>
    <div class="title-rule"></div>
    <div class="title-author">شذى ياسر الجوبحي</div>
    <div class="title-author-role">اليمن</div>
  </div>
  <div class="title-meta">الطبعة الأولى</div>
</section>''')

# Page 5: Copyright
body_parts.append('''<section class="copyright-page">
  <div class="copyright-block">
    <p class="cr-strong">انتروبيا الحنين</p>
    <p>رواية</p>
    <div class="cr-rule"></div>
    <p>تأليف: <span class="cr-strong">شذى ياسر الجوبحي</span></p>
    <p>اليمن</p>
    <div class="cr-rule"></div>
    <p>الطبعة الأولى · ٢٠٢٦</p>
    <p>جميع الحقوق محفوظة للمؤلفة</p>
    <p>يمنع النسخ أو الاقتباس دون إذن خطّي</p>
    <div class="cr-rule"></div>
    <p>التصميم والإخراج الفني:</p>
    <p class="cr-strong">استوديو الإخراج الأدبي</p>
    <div class="cr-rule"></div>
    <p class="cr-contact">+967 775 863 594</p>
    <p class="cr-isbn">ISBN · PENDING</p>
  </div>
</section>''')

# Page 6: Dedication
ded_lines_html = '\n'.join(f'<p>{line}</p>' for line in book['dedication']['lines'])
body_parts.append(f'''<section class="dedication-page">
  <div class="dedication-mark">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
      <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>
      <line x1="12" y1="0" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="24"/>
      <line x1="0" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="24" y2="12"/>
    </svg>
  </div>
  <div class="dedication-text">{ded_lines_html}</div>
  <div class="dedication-coda">معكم صِرتُ نظامًا لا يفنى،<br>حبّه ثابتٌ وطاقته لا تنضب.</div>
  <div class="dedication-sign">شذى ياسر</div>
</section>''')

# Page 7+: Table of contents
toc_items = []
toc_items.append('<li class="toc-item"><span class="toc-num">٠</span><span class="toc-text">المقدمة</span></li>')
for i, ch in enumerate(book['chapters']):
    title = ch['title']
    if ' - ' in title:
        main, sub = title.split(' - ', 1)
        display = f'{main} — {sub}'
    else:
        display = title
    toc_items.append(f'<li class="toc-item"><span class="toc-num">{i+1:02d}</span><span class="toc-text">{display}</span></li>')
toc_items.append('<li class="toc-item toc-appendix"><span class="toc-num">★</span><span class="toc-text">أقباس وملاحق الرواية</span></li>')
for i, ap in enumerate(book['appendices']):
    toc_items.append(f'<li class="toc-item toc-appendix"><span class="toc-num">★</span><span class="toc-text">{ap["title"]}</span></li>')

toc_html = '\n'.join(toc_items)
body_parts.append(f'''<section class="toc-page">
  <h2 class="toc-title">المحتويات</h2>
  <ul class="toc-list">{toc_html}</ul>
</section>''')

# === Add a flyleaf before preface for breathing room ===
body_parts.append('<section class="flyleaf"></section>')

# === Preface ===
preface_blocks_html = '\n'.join(
    f'<p class="{"first-para" if i==0 else ""}">{b["text"]}</p>' if b['type']=='p'
    else f'<div class="voice">{b["text"]}</div>'
    for i, b in enumerate(book['preface']['blocks'])
)
body_parts.append(f'''<section class="preface-section">
  <div class="preface-epigraph">{book["preface"]["epigraph"]}</div>
  <h2 class="preface-title">مقدمة</h2>
  <div class="preface-body">{preface_blocks_html}</div>
  <div class="preface-sign"><span class="sig-name">شذى</span>الكون: الأرض.<br>الساعة ٣:١٧ فجرًا.</div>
</section>''')

# === Chapters with qibas ===
CHAPTER_ORDINALS = ['الأول','الثاني','الثالث','الرابع','الخامس','السادس','السابع']

for i, ch in enumerate(book['chapters']):
    # Chapter opener (full page)
    title = ch['title']
    if ' - ' in title:
        main, sub = title.split(' - ', 1)
    else:
        main, sub = title, ''
    
    body_parts.append(f'''<section class="chapter-opener" data-chapter="{i+1}">
  <div class="chapter-ghost-num">{i+1:02d}</div>
  <svg class="chapter-orbit" viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="0.3">
    <circle cx="100" cy="100" r="95"/>
    <circle cx="100" cy="100" r="72"/>
    <circle cx="100" cy="100" r="48"/>
    <ellipse cx="100" cy="100" rx="95" ry="40" transform="rotate(15 100 100)"/>
    <ellipse cx="100" cy="100" rx="95" ry="40" transform="rotate(-25 100 100)"/>
    <circle cx="100" cy="5" r="2" fill="currentColor" stroke="none"/>
  </svg>
  <div class="chapter-content">
    <div class="chapter-label">الفصل {CHAPTER_ORDINALS[i] if i < len(CHAPTER_ORDINALS) else i+1}</div>
    <div class="chapter-num-small">{i+1:02d}</div>
    <h2 class="chapter-title">{main}{f'<span class="chapter-sub">{sub}</span>' if sub else ''}</h2>
    <div class="chapter-title-rule"></div>
    {f'<div class="chapter-epigraph">{ch["epigraph"]}</div>' if ch.get("epigraph") else ''}
  </div>
</section>''')

    # Chapter body (flows naturally — NO break-after)
    body_blocks = []
    for j, b in enumerate(ch['blocks']):
        if b['type'] == 'p':
            cls = 'first-para' if j == 0 else ''
            body_blocks.append(f'<p class="{cls}">{b["text"]}</p>')
        elif b['type'] == 'voice':
            body_blocks.append(f'<p class="dialogue">{b["text"]}</p>')
        elif b['type'] == 'whisper':
            body_blocks.append(f'<div class="whisper">{b["text"]}</div>')
        elif b['type'] == 'letter':
            body_blocks.append(f'<div class="letter">{b["text"]}</div>')
        elif b['type'] == 'signature':
            body_blocks.append(f'<div class="signature">{b["text"]}</div>')
    
    body_parts.append(f'<section class="chapter-body" data-chapter-title="{main}">{"".join(body_blocks)}</section>')
    
    # Qibas page after chapter (full page)
    if ch.get('qibas'):
        qibas = ch['qibas']
        qibas_blocks_html = ''
        for b in qibas['blocks']:
            if b['type'] == 'whisper':
                qibas_blocks_html += f'<div class="qibas-text">{b["text"]}</div>'
            elif b['type'] == 'signature':
                qibas_blocks_html += f'<div class="qibas-sign">{b["text"]}</div>'
            else:
                qibas_blocks_html += f'<div class="qibas-text">{b["text"]}</div>'
        
        body_parts.append(f'''<section class="qibas-page">
  <div class="qibas-ornament">
    <svg viewBox="0 0 60 12" fill="none" stroke="currentColor" stroke-width="0.8">
      <circle cx="6" cy="6" r="1.5"/><line x1="14" y1="6" x2="26" y2="6"/>
      <circle cx="30" cy="6" r="2"/><line x1="34" y1="6" x2="46" y2="6"/><circle cx="54" cy="6" r="1.5"/>
    </svg>
  </div>
  <div class="qibas-label">{qibas["title"]}</div>
  {qibas_blocks_html}
</section>''')

# === Appendices ===
body_parts.append('<section class="appendix-divider"><div class="appendix-divider-mark">★</div><div class="appendix-divider-label">أقباس وملاحق الرواية</div></section>')

for ap in book['appendices']:
    body_parts.append(f'''<section class="appendix-opener">
  <div class="appendix-label">ملحق</div>
  <h2 class="appendix-title">{ap["title"]}</h2>
  <div class="chapter-title-rule"></div>
</section>''')
    
    ap_blocks = []
    if ap.get('intro'):
        for j, b in enumerate(ap['intro']):
            if b['type'] == 'p':
                cls = 'first-para' if j == 0 else ''
                ap_blocks.append(f'<p class="{cls}">{b["text"]}</p>')
            elif b['type'] == 'voice':
                ap_blocks.append(f'<p class="dialogue">{b["text"]}</p>')
            elif b['type'] == 'whisper':
                ap_blocks.append(f'<div class="whisper">{b["text"]}</div>')
            elif b['type'] == 'signature':
                ap_blocks.append(f'<div class="signature">{b["text"]}</div>')
    
    for ss in ap['sub_sections']:
        if ss.get('title'):
            ap_blocks.append(f'<h3 class="sub-section-title">{ss["title"]}</h3>')
        for j, b in enumerate(ss['blocks']):
            if b['type'] == 'p':
                cls = 'first-para' if j == 0 and not ss.get('title') else ''
                ap_blocks.append(f'<p class="{cls}">{b["text"]}</p>')
            elif b['type'] == 'voice':
                ap_blocks.append(f'<p class="dialogue">{b["text"]}</p>')
            elif b['type'] == 'whisper':
                ap_blocks.append(f'<div class="whisper">{b["text"]}</div>')
            elif b['type'] == 'signature':
                ap_blocks.append(f'<div class="signature">{b["text"]}</div>')
    
    body_parts.append(f'<section class="appendix-body">{"".join(ap_blocks)}</section>')

# === End colophon ===
body_parts.append('''<section class="colophon">
  <div class="colophon-mark">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2">
      <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3" fill="currentColor" stroke="none"/>
      <line x1="12" y1="0" x2="12" y2="6"/><line x1="12" y1="18" x2="12" y2="24"/>
      <line x1="0" y1="12" x2="6" y2="12"/><line x1="18" y1="12" x2="24" y2="12"/>
    </svg>
  </div>
  <div class="colophon-text">
    انتروبيا الحنين<br>
    رواية · شذى ياسر الجوبحي<br>
    الطبعة الأولى · ٢٠٢٦
  </div>
  <div class="colophon-quote">لا شيء يُفنى، لكن كل شيء يتغيّر.</div>
</section>''')

body_html = '\n\n'.join(body_parts)

# === CSS — Classic Literary Design ===
css = '''
/* ============================================================
   انتروبيا الحنين — V3 Classic Literary Design
   A5 (148×210mm) + 3mm bleed = 154×216mm
   Paged.js polyfill for running headers + page numbers
   ============================================================ */

@page {
  size: 154mm 216mm;
  margin: 24mm 20mm 24mm 26mm;   /* top outer bottom inner (gutter) — generous for classic feel */
  
  @top-center {
    content: string(chapter-title);
    font-family: 'IBM Plex Sans Arabic', sans-serif;
    font-size: 8.5pt;
    font-weight: 400;
    color: #8A847A;
    letter-spacing: 0.1em;
    margin-bottom: 6mm;
  }
  
  @bottom-center {
    content: counter(page);
    font-family: 'IBM Plex Sans Arabic', sans-serif;
    font-size: 9pt;
    font-weight: 400;
    color: #8A847A;
    margin-top: 6mm;
  }
}

/* No header/footer on front matter pages */
@page front-matter {
  @top-center { content: none; }
  @bottom-center { content: none; }
}

/* No header/footer on chapter opener pages */
@page chapter-opener {
  @top-center { content: none; }
  @bottom-center { content: none; }
}

/* No page number on title/copyright/dedication */
@page :first {
  margin: 0;
  @top-center { content: none; }
  @bottom-center { content: none; }
}

@page no-footer {
  @top-center { content: none; }
  @bottom-center { content: none; }
}

:root {
  --bg:        #F4F1EA;
  --bg-soft:   #EFEBE1;
  --ink:       #1B1A17;
  --ink-soft:  #4A463E;
  --ink-mute:  #8A847A;
  --rule:      #D9D3C5;
  --brass:     #8C6B3F;
  --brass-soft:#B89968;
  --brass-glow:#E4C988;
  --f-display: 'Reem Kufi', 'IBM Plex Sans Arabic', serif;
  --f-head:    'IBM Plex Sans Arabic', 'Noto Naskh Arabic', sans-serif;
  --f-body:    'Noto Naskh Arabic', 'IBM Plex Sans Arabic', serif;
  --f-quote:   'Amiri', 'Noto Naskh Arabic', serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--f-body);
  font-size: 14pt;
  line-height: 2.1;
  direction: rtl;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

@media screen {
  html { background: #2a2826; display: flex; justify-content: center; }
  body { background: var(--bg); margin: 24px auto; box-shadow: 0 4px 32px rgba(0,0,0,0.4); }
}

/* === FLYLEAF (blank page) === */
.flyleaf {
  page: no-footer;
  min-height: 170mm;
}

/* === HALF-TITLE === */
.half-title-page {
  page: no-footer;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}
.half-title {
  font-family: var(--f-display);
  font-size: 36pt;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: 0.02em;
}
.half-title-sub {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 14pt;
  color: var(--ink-soft);
  margin-top: 8mm;
}

/* === TITLE PAGE === */
.title-page {
  page: no-footer;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  text-align: center;
  padding: 30mm 24mm;
}
.title-publisher {
  font-family: var(--f-head);
  font-size: 9pt;
  font-weight: 400;
  letter-spacing: 0.4em;
  color: var(--ink-mute);
  text-transform: uppercase;
}
.title-main {
  font-family: var(--f-display);
  font-size: 42pt;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.1;
  margin: 0;
}
.title-sub {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 14pt;
  color: var(--ink-soft);
  margin-top: 6mm;
}
.title-rule {
  width: 24mm;
  height: 0.6pt;
  background: var(--brass);
  margin: 12mm auto;
}
.title-author {
  font-family: var(--f-head);
  font-size: 13pt;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: 0.06em;
}
.title-author-role {
  font-family: var(--f-body);
  font-size: 10pt;
  color: var(--ink-mute);
  margin-top: 2mm;
}
.title-meta {
  font-family: var(--f-head);
  font-size: 8.5pt;
  font-weight: 300;
  color: var(--ink-mute);
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

/* === COPYRIGHT === */
.copyright-page {
  page: no-footer;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  text-align: center;
  padding: 50mm 24mm 24mm;
}
.copyright-block {
  font-family: var(--f-head);
  font-size: 9pt;
  line-height: 1.9;
  color: var(--ink-soft);
}
.copyright-block p { margin: 1mm 0; }
.copyright-block .cr-strong { color: var(--ink); font-weight: 500; }
.copyright-block .cr-rule {
  width: 16mm; height: 0.4pt; background: var(--rule); margin: 3mm auto;
}
.copyright-block .cr-isbn {
  font-weight: 300; font-size: 8.5pt; color: var(--ink-mute); letter-spacing: 0.15em;
}
.copyright-block .cr-contact {
  font-size: 9pt; color: var(--ink); direction: ltr; unicode-bidi: isolate; margin-top: 2mm;
}

/* === DEDICATION === */
.dedication-page {
  page: no-footer;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 40mm 28mm;
}
.dedication-mark {
  width: 10mm; height: 10mm; margin-bottom: 14mm; color: var(--brass); opacity: 0.7;
}
.dedication-mark svg { width: 100%; height: 100%; }
.dedication-text {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 13pt;
  line-height: 2.0;
  color: var(--ink);
  max-width: 100mm;
}
.dedication-text p { margin-bottom: 1.5mm; }
.dedication-coda {
  font-family: var(--f-display);
  font-size: 12pt;
  color: var(--brass);
  margin-top: 14mm;
  letter-spacing: 0.06em;
  line-height: 1.6;
}
.dedication-sign {
  font-family: var(--f-head);
  font-size: 9pt;
  color: var(--ink-mute);
  margin-top: 8mm;
  letter-spacing: 0.2em;
}

/* === TOC === */
.toc-page {
  page: no-footer;
  padding: 8mm 0;
}
.toc-title {
  font-family: var(--f-display);
  font-size: 22pt;
  font-weight: 500;
  color: var(--ink);
  text-align: center;
  letter-spacing: 0.05em;
  margin-bottom: 14mm;
}
.toc-title::after {
  content: ""; display: block; width: 20mm; height: 0.5pt;
  background: var(--brass); margin: 5mm auto 0;
}
.toc-list { list-style: none; padding: 0; font-family: var(--f-head); }
.toc-item {
  display: flex; align-items: baseline;
  font-size: 12pt; color: var(--ink);
  padding: 3mm 0; border-bottom: 0.3pt solid var(--rule);
}
.toc-item.toc-appendix { margin-top: 3mm; color: var(--ink-soft); }
.toc-item .toc-num {
  font-family: var(--f-display); font-size: 13pt; font-weight: 600;
  color: var(--brass); width: 14mm; flex-shrink: 0;
}
.toc-item .toc-text { font-weight: 500; }

/* === PREFACE === */
.preface-section {
  break-before: page;
  page-break-before: always;
  string-set: chapter-title "مقدمة";
}
.preface-epigraph {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 13pt;
  line-height: 1.9;
  color: var(--ink-soft);
  text-align: center;
  max-width: 100mm;
  margin: 0 auto 12mm;
  padding: 0 6mm;
}
.preface-epigraph::before, .preface-epigraph::after {
  content: ""; display: block; width: 12mm; height: 0.4pt;
  background: var(--brass); margin: 5mm auto;
}
.preface-title {
  font-family: var(--f-display);
  font-size: 16pt;
  font-weight: 500;
  color: var(--ink);
  text-align: center;
  letter-spacing: 0.1em;
  margin-bottom: 10mm;
}
.preface-body p {
  font-family: var(--f-body);
  font-size: 13pt;
  line-height: 2.0;
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 3.5mm;
  text-indent: 6mm;
  orphans: 3; widows: 3;
}
.preface-body p.first-para { text-indent: 0; }
.preface-sign {
  font-family: var(--f-quote); font-style: italic; font-size: 11pt;
  color: var(--ink-soft); text-align: center; margin-top: 12mm; line-height: 1.7;
}
.preface-sign .sig-name {
  display: block; font-family: var(--f-display); font-style: normal;
  font-size: 13pt; color: var(--brass); margin-bottom: 1mm;
}

/* === CHAPTER OPENER === */
.chapter-opener {
  page: chapter-opener;
  break-before: page;
  page-break-before: always;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
  string-set: chapter-title content();
}
.chapter-ghost-num {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -55%);
  font-family: var(--f-display);
  font-size: 240pt;
  font-weight: 600;
  color: var(--brass);
  opacity: 0.08;
  line-height: 1;
  z-index: 0;
  direction: ltr;
}
.chapter-orbit {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 120mm; height: 120mm;
  z-index: 0; opacity: 0.3; color: var(--brass);
}
.chapter-content {
  position: relative; z-index: 1; text-align: center; padding: 0 18mm;
}
.chapter-label {
  font-family: var(--f-head); font-size: 9pt; font-weight: 500;
  letter-spacing: 0.4em; color: var(--brass); text-transform: uppercase;
  margin-bottom: 8mm;
}
.chapter-num-small {
  font-family: var(--f-display); font-size: 18pt; font-weight: 500;
  color: var(--ink-mute); letter-spacing: 0.2em; margin-bottom: 4mm; direction: ltr;
}
.chapter-title {
  font-family: var(--f-display); font-size: 26pt; font-weight: 500;
  color: var(--ink); line-height: 1.25; max-width: 100mm;
  margin: 6mm auto 10mm; letter-spacing: 0;
}
.chapter-title .chapter-sub {
  display: block; font-size: 16pt; font-weight: 400;
  color: var(--ink-soft); margin-top: 3mm; font-style: italic; font-family: var(--f-quote);
}
.chapter-title-rule {
  width: 22mm; height: 0.6pt; background: var(--brass); margin: 0 auto 10mm;
}
.chapter-epigraph {
  font-family: var(--f-quote); font-style: italic; font-size: 11pt;
  line-height: 1.8; color: var(--ink-soft); max-width: 80mm; margin: 0 auto;
}

/* === CHAPTER BODY (flows naturally) === */
.chapter-body {
  break-before: page;
  page-break-before: always;
  /* NO break-after — let content flow to fill pages naturally */
  string-set: chapter-title attr(data-chapter-title);
}
.chapter-body p {
  font-family: var(--f-body);
  font-size: 14pt;
  line-height: 2.1;
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 4mm;
  text-indent: 6mm;
  orphans: 3; widows: 3;
}
.chapter-body p.first-para { text-indent: 0; }
.chapter-body p.first-para::first-letter {
  font-family: var(--f-display);
  font-size: 36pt;
  font-weight: 600;
  color: var(--brass);
  float: right;
  line-height: 0.9;
  margin: 2mm 0 0 3mm;
}

/* Dialogue — each speaker in own paragraph */
.chapter-body p.dialogue,
.appendix-body p.dialogue {
  font-family: var(--f-body);
  font-size: 14pt;
  line-height: 2.1;
  color: var(--ink);
  text-align: justify;
  text-indent: 6mm;
  margin: 0 0 3.5mm;
  orphans: 2; widows: 2;
}

/* Whisper — centered philosophical lines */
.chapter-body .whisper,
.appendix-body .whisper {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 14pt;
  line-height: 2.0;
  color: var(--ink-soft);
  text-align: center;
  margin: 5mm auto;
  max-width: 85mm;
  padding: 0 4mm;
  text-indent: 0;
  break-inside: avoid;
}

/* Signature */
.chapter-body .signature,
.appendix-body .signature {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 11pt;
  color: var(--brass);
  text-align: center;
  margin: 5mm 0 3mm;
  letter-spacing: 0.05em;
}

/* === QIBAS PAGE === */
.qibas-page {
  page: chapter-opener;
  break-before: page;
  page-break-before: always;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 24mm;
}
.qibas-ornament {
  width: 30mm; height: 6mm; margin-bottom: 16mm; color: var(--brass); opacity: 0.6;
}
.qibas-ornament svg { width: 100%; height: 100%; }
.qibas-label {
  font-family: var(--f-display);
  font-size: 16pt;
  font-weight: 500;
  color: var(--brass);
  letter-spacing: 0.1em;
  margin-bottom: 16mm;
}
.qibas-text {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 16pt;
  line-height: 1.9;
  color: var(--ink);
  max-width: 90mm;
  margin-bottom: 8mm;
}
.qibas-sign {
  font-family: var(--f-quote);
  font-style: italic;
  font-size: 13pt;
  color: var(--brass);
  margin-top: 8mm;
}

/* === APPENDIX DIVIDER === */
.appendix-divider {
  page: chapter-opener;
  break-before: page;
  page-break-before: always;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}
.appendix-divider-mark {
  font-size: 36pt;
  color: var(--brass);
  margin-bottom: 16mm;
  opacity: 0.6;
}
.appendix-divider-label {
  font-family: var(--f-display);
  font-size: 24pt;
  font-weight: 500;
  color: var(--ink);
  letter-spacing: 0.05em;
}

/* === APPENDIX OPENER === */
.appendix-opener {
  page: chapter-opener;
  break-before: page;
  page-break-before: always;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 0 24mm;
  string-set: chapter-title content();
}
.appendix-label {
  font-family: var(--f-head); font-size: 9pt; font-weight: 500;
  letter-spacing: 0.4em; color: var(--brass); text-transform: uppercase;
  margin-bottom: 8mm;
}
.appendix-title {
  font-family: var(--f-display); font-size: 22pt; font-weight: 500;
  color: var(--ink); line-height: 1.25; max-width: 100mm; margin: 0 auto 10mm;
}

/* === APPENDIX BODY === */
.appendix-body {
  break-before: page;
  page-break-before: always;
  string-set: chapter-title "ملحق";
}
.appendix-body p {
  font-family: var(--f-body);
  font-size: 14pt;
  line-height: 2.1;
  color: var(--ink);
  text-align: justify;
  text-justify: inter-word;
  margin: 0 0 3.5mm;
  text-indent: 6mm;
  orphans: 3; widows: 3;
}
.appendix-body p.first-para { text-indent: 0; }
.appendix-body p.first-para::first-letter {
  font-family: var(--f-display);
  font-size: 36pt;
  font-weight: 600;
  color: var(--brass);
  float: right;
  line-height: 0.9;
  margin: 2mm 0 0 3mm;
}
.sub-section-title {
  font-family: var(--f-display); font-size: 16pt; font-weight: 500;
  color: var(--brass); text-align: center; margin: 14mm 0 8mm;
  letter-spacing: 0.05em; break-after: avoid;
}
.sub-section-title::before, .sub-section-title::after {
  content: ""; display: inline-block; width: 8mm; height: 0.4pt;
  background: var(--brass); vertical-align: middle; margin: 0 4mm; opacity: 0.6;
}

/* === COLOPHON === */
.colophon {
  page: no-footer;
  break-before: page;
  page-break-before: always;
  min-height: 170mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}
.colophon-mark {
  width: 12mm; height: 12mm; margin-bottom: 16mm; color: var(--brass); opacity: 0.5;
}
.colophon-mark svg { width: 100%; height: 100%; }
.colophon-text {
  font-family: var(--f-quote); font-style: italic; font-size: 13pt;
  color: var(--ink-soft); line-height: 1.9; margin-bottom: 12mm;
}
.colophon-quote {
  font-family: var(--f-display); font-size: 14pt; color: var(--brass);
  letter-spacing: 0.05em;
}

/* === PAGINATION SAFETY === */
h1, h2, h3 { break-after: avoid; page-break-after: avoid; }
.whisper, .signature, .qibas-text { break-inside: avoid; page-break-inside: avoid; }
'''

# === Assemble final HTML ===
html = f'''<!DOCTYPE html>
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
<body>
{body_html}
</body>
</html>'''

OUT_PRINT.write_text(html, encoding='utf-8')
print(f'✓ V3 Print HTML: {OUT_PRINT}  ({OUT_PRINT.stat().st_size/1024:.1f} KB)')
print(f'  Body sections: {len(body_parts)}')
