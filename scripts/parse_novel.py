#!/usr/bin/env python3
"""
Convert the cleaned novel markdown into a structured JSON + HTML for the book.

This script:
1. Parses /tmp/novel_clean.md into structured sections (dedication, preface, chapters, appendices)
2. Detects special text types within paragraphs:
   - Dialogues (quoted with "...") → wrapped in .voice
   - Letters/written notes (multi-line quoted blocks) → wrapped in .letter
   - Philosophical whispers (italic, standalone) → wrapped in .whisper
3. Outputs:
   - /home/z/my-project/build/v2/book-data.json — structured data for the web reader
   - /home/z/my-project/build/v2/book-content.html — HTML fragment for the print interior
"""
import json
import re
from pathlib import Path

SRC = Path('/tmp/novel_clean.md')
OUT_JSON = Path('/home/z/my-project/build/v2/book-data.json')
OUT_HTML = Path('/home/z/my-project/build/v2/book-content.html')


def clean_text(t: str) -> str:
    """Remove residual pandoc artifacts."""
    # Remove stray backticks before diacritics
    t = re.sub(r'\\`', '', t)
    # Remove stray backticks (standalone)
    t = re.sub(r'`', '', t)
    # Remove empty [] markers (often left by pandoc for empty paragraphs)
    t = re.sub(r'^\[\]\s*$', '', t, flags=re.MULTILINE)
    # Remove inline empty []
    t = re.sub(r'\[\]', '', t)
    # Remove the #والدة_دُجى hashtag line and #شذى_ياسر
    t = re.sub(r'^\s*#\*\*[^*]*\*\*\s*$', '', t, flags=re.MULTILINE)
    # Remove leftover *** wrappers around signatures like ***- شذى***
    # Convert ***- شذى*** to - شذى (signature)
    t = re.sub(r'\*\*\*-\s*([^*]+?)\*\*\*', r'- \1', t)
    # Remove ** wrappers around headings (we'll handle headings separately)
    # But keep ** for bold inline
    # Remove leading/trailing whitespace per line
    t = '\n'.join(line.rstrip() for line in t.split('\n'))
    return t.strip()


def parse_paragraph_to_blocks(para: str) -> list:
    """
    Parse a paragraph (possibly multi-line) into typed blocks.

    Heuristics:
    - If paragraph is entirely within "..." (starts and ends with quote) → voice
    - If paragraph contains a quote that's >80 chars and stands alone → voice
    - Otherwise → p (with embedded dialogue inline)
    """
    para = clean_text(para)
    if not para:
        return []

    # Strip markdown italic/ bold wrappers for detection
    stripped = para.strip()

    # Skip stray hashtag lines like "**#والدة_دُجى**"
    if re.match(r'^\*{0,2}#\S+\*{0,2}$', stripped):
        return []

    # Skip signature lines like "- شذى" or "- شذى ياسر" — treat as whisper signature
    if re.match(r'^-\s*شذى', stripped):
        return [{'type': 'signature', 'text': stripped}]

    # Check if entire paragraph is a single quote (voice)
    if stripped.startswith('"') and stripped.endswith('"') and stripped.count('"') == 2:
        return [{'type': 'voice', 'text': stripped[1:-1]}]

    # Check if it's an italic line (whisper) — starts and ends with *
    if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
        inner = stripped.strip('*').strip()
        if inner:
            return [{'type': 'whisper', 'text': inner}]

    # Default: regular paragraph
    return [{'type': 'p', 'text': para}]


def split_paragraphs(text: str) -> list:
    """Split text into paragraphs by double newlines."""
    paras = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paras if p.strip()]


def parse_chapter(title: str, body: str) -> dict:
    """Parse a chapter section."""
    # Extract chapter number and title
    # Patterns: "الفصل الأول: الكف التي لا تتحلل" or "الفصل السابع والأخير: الخط 0 - قانون الذوبان"
    m = re.match(r'الفصل\s+([^:]+):\s*(.+)', title)
    if m:
        chapter_ord = m.group(1).strip()
        chapter_title = m.group(2).strip()
    else:
        chapter_ord = ''
        chapter_title = title

    # Extract epigraph (italic line at start, if any)
    epigraph = None
    blocks = []
    paras = split_paragraphs(body)

    for i, para in enumerate(paras):
        # Skip empty
        if not para.strip():
            continue
        # Detect italic epigraph at chapter start
        if i == 0 and para.strip().startswith('*') and para.strip().endswith('*') and not para.strip().startswith('**'):
            epigraph = para.strip().strip('*').strip()
            continue
        blocks.extend(parse_paragraph_to_blocks(para))

    return {
        'num': chapter_ord,
        'title': chapter_title,
        'epigraph': epigraph,
        'blocks': blocks,
    }


def parse_appendix(title: str, body: str) -> dict:
    """Parse an appendix section (ملحق)."""
    blocks = []
    # Sub-headings (قُبس) become sub-section markers
    sub_sections = []

    # Split by ### sub-headings
    parts = re.split(r'\n###\s+\*\*([^*]+)\*\*\s*\n', body)
    # parts[0] = before any ###, then alternating: title, body, title, body...

    # First part (intro before any ###)
    intro = parts[0].strip()
    if intro:
        for para in split_paragraphs(intro):
            blocks.extend(parse_paragraph_to_blocks(para))

    if blocks:
        sub_sections.append({'title': None, 'blocks': blocks})

    # Sub-sections
    for i in range(1, len(parts), 2):
        sub_title = parts[i].strip()
        sub_body = parts[i+1] if i+1 < len(parts) else ''
        sub_blocks = []
        for para in split_paragraphs(sub_body):
            sub_blocks.extend(parse_paragraph_to_blocks(para))
        sub_sections.append({'title': sub_title, 'blocks': sub_blocks})

    return {
        'title': title,
        'sub_sections': sub_sections,
    }


def main():
    content = clean_text(SRC.read_text(encoding='utf-8'))

    # First, normalize: convert "# **أقباس وملاحق الرواية**" (H1) to H2 so it's captured
    content_normalized = re.sub(
        r'\n#\s+\*\*أقباس وملاحق الرواية\*\*\s*\n',
        '\n## **أقباس وملاحق الرواية**\n',
        content
    )

    # Split into top-level sections by ## headings
    # parts[0] = preamble, then alternating: title, body
    parts = re.split(r'\n##\s+\*\*([^*]+)\*\*\s*\n', content_normalized)

    preamble = parts[0]
    sections_raw = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i+1] if i+1 < len(parts) else ''
        sections_raw.append((title, body))

    # Parse preamble (dedication + preface)
    dedication = None
    preface = None
    preface_epigraph = None

    # Preamble contains "# **إهداء**" and "# **مقدمة**" as H1
    h1_parts = re.split(r'\n#\s+\*\*([^*]+)\*\*\s*\n', preamble)
    # h1_parts[0] = title block (book title), then alternating: title, body

    # Parse book title from h1_parts[0]
    book_title_block = h1_parts[0].strip()
    # Extract title and author
    title_match = re.search(r'\*\*([^*]+)\*\*', book_title_block)
    raw_title = title_match.group(1).strip() if title_match else 'انتروبيا الحنين'
    # Normalize the title (remove decorative spaces in أتروبيا)
    book_title = 'انتروبيا الحنين'
    book_author = 'شذى ياسر الجوبحي'

    for i in range(1, len(h1_parts), 2):
        h1_title = h1_parts[i].strip()
        h1_body = h1_parts[i+1] if i+1 < len(h1_parts) else ''
        if 'إهداء' in h1_title:
            # Parse dedication
            ded_paras = split_paragraphs(h1_body)
            ded_lines = []
            for p in ded_paras:
                p_clean = clean_text(p)
                if p_clean:
                    # Remove #شذى_ياسر hashtag and #والدة_دُجى hashtag
                    p_clean = re.sub(r'#\S+', '', p_clean).strip()
                    # Strip ** wrappers
                    p_clean = re.sub(r'^\*\*|\*\*$', '', p_clean).strip()
                    if p_clean:
                        ded_lines.append(p_clean)
            dedication = {'lines': ded_lines}
        elif 'مقدمة' in h1_title:
            # Parse preface — extract epigraph (italic line with "لا شيء يُفنى")
            pre_paras = split_paragraphs(h1_body)
            preface_blocks = []
            for j, p in enumerate(pre_paras):
                p_clean = clean_text(p)
                if not p_clean:
                    continue
                # Detect epigraph (italic, contains "لا شيء يُفنى")
                if j < 3 and ('لا شيء يُفنى' in p_clean or 'لا شيء يفنى' in p_clean):
                    # Strip * markers
                    ep = p_clean.strip('*').strip().strip('"').strip()
                    preface_epigraph = ep
                    continue
                preface_blocks.extend(parse_paragraph_to_blocks(p))
            preface = {'epigraph': preface_epigraph, 'blocks': preface_blocks}

    # Parse chapters and appendices
    chapters = []
    appendices = []
    section_divider_idx = None

    for i, (title, body) in enumerate(sections_raw):
        if title.startswith('الفصل'):
            # Trim chapter body: remove any trailing ### sub-headings (they belong to appendices)
            # Find the first ### that's a قُبس and cut there
            cut_match = re.search(r'\n###\s+\*\*قُبس', body)
            if cut_match:
                body = body[:cut_match.start()]
            chapters.append(parse_chapter(title, body))
        elif 'أقباس وملاحق' in title:
            appendix_obj = {
                'title': 'أقباس وملاحق الرواية',
                'intro': None,
                'sub_sections': [],
            }
            sub_parts = re.split(r'\n###\s+\*\*([^*]+)\*\*\s*\n', body)
            intro = sub_parts[0].strip()
            # The intro may contain the first قُبس (which is split as a paragraph starting with "### **قُبس أول**")
            # Let's check if intro starts with a قُبس heading pattern
            if intro:
                intro_blocks = []
                for para in split_paragraphs(intro):
                    p_clean = clean_text(para)
                    if not p_clean:
                        continue
                    # If the paragraph itself is a heading like "### **قُبس أول**", extract it as a sub-section
                    heading_match = re.match(r'^###\s+\*\*([^*]+)\*\*\s*$', p_clean)
                    if heading_match:
                        # This is a sub-heading embedded in intro — start a new sub-section
                        appendix_obj['sub_sections'].append({
                            'title': heading_match.group(1).strip(),
                            'blocks': []
                        })
                    else:
                        if appendix_obj['sub_sections']:
                            # Append to last sub-section
                            appendix_obj['sub_sections'][-1]['blocks'].extend(parse_paragraph_to_blocks(p_clean))
                        else:
                            intro_blocks.extend(parse_paragraph_to_blocks(p_clean))
                if intro_blocks:
                    appendix_obj['intro'] = intro_blocks
            for j in range(1, len(sub_parts), 2):
                sub_title = sub_parts[j].strip()
                sub_body = sub_parts[j+1] if j+1 < len(sub_parts) else ''
                sub_blocks = []
                for para in split_paragraphs(sub_body):
                    sub_blocks.extend(parse_paragraph_to_blocks(para))
                appendix_obj['sub_sections'].append({'title': sub_title, 'blocks': sub_blocks})
            appendices.append(appendix_obj)
        elif title.startswith('ملحق'):
            appendix_obj = {
                'title': title,
                'intro': None,
                'sub_sections': [],
            }
            sub_parts = re.split(r'\n###\s+\*\*([^*]+)\*\*\s*\n', body)
            intro = sub_parts[0].strip()
            if intro:
                appendix_obj['intro'] = []
                for para in split_paragraphs(intro):
                    appendix_obj['intro'].extend(parse_paragraph_to_blocks(para))
            for j in range(1, len(sub_parts), 2):
                sub_title = sub_parts[j].strip()
                sub_body = sub_parts[j+1] if j+1 < len(sub_parts) else ''
                sub_blocks = []
                for para in split_paragraphs(sub_body):
                    sub_blocks.extend(parse_paragraph_to_blocks(para))
                appendix_obj['sub_sections'].append({'title': sub_title, 'blocks': sub_blocks})
            appendices.append(appendix_obj)

    # Assemble the book
    book = {
        'title': book_title,
        'subtitle': 'رواية',
        'author': book_author,
        'year': '٢٠٢٦',
        'dedication': dedication,
        'preface': preface,
        'chapters': chapters,
        'appendices': appendices,
    }

    # Stats
    total_blocks = 0
    if preface:
        total_blocks += len(preface['blocks'])
    for ch in chapters:
        total_blocks += len(ch['blocks'])
    for ap in appendices:
        if ap['intro']:
            total_blocks += len(ap['intro'])
        for ss in ap['sub_sections']:
            total_blocks += len(ss['blocks'])

    print(f"=== Book parsed ===")
    print(f"  Title: {book_title}")
    print(f"  Author: {book_author}")
    print(f"  Dedication lines: {len(dedication['lines']) if dedication else 0}")
    print(f"  Preface blocks: {len(preface['blocks']) if preface else 0}")
    print(f"  Chapters: {len(chapters)}")
    for ch in chapters:
        print(f"    {ch['num']:15s} | {ch['title'][:40]:40s} | {len(ch['blocks'])} blocks")
    print(f"  Appendices: {len(appendices)}")
    for ap in appendices:
        ss_count = len(ap['sub_sections'])
        print(f"    {ap['title'][:50]:50s} | {ss_count} sub-sections")
    print(f"  Total text blocks: {total_blocks}")

    # Save JSON
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n  ✓ JSON saved: {OUT_JSON}")

    # Also save a quick HTML preview fragment
    html_parts = []
    if preface:
        html_parts.append('<section class="preface">')
        if preface.get('epigraph'):
            html_parts.append(f'  <div class="epigraph">{preface["epigraph"]}</div>')
        html_parts.append('  <h2>مقدمة</h2>')
        for b in preface['blocks']:
            if b['type'] == 'p':
                html_parts.append(f'  <p>{b["text"]}</p>')
            elif b['type'] == 'voice':
                html_parts.append(f'  <div class="voice">{b["text"]}</div>')
            elif b['type'] == 'whisper':
                html_parts.append(f'  <div class="whisper">{b["text"]}</div>')
        html_parts.append('</section>')
    for ch in chapters:
        html_parts.append('<section class="chapter">')
        html_parts.append(f'  <h2>{ch["title"]}</h2>')
        if ch.get('epigraph'):
            html_parts.append(f'  <div class="epigraph">{ch["epigraph"]}</div>')
        for b in ch['blocks']:
            if b['type'] == 'p':
                html_parts.append(f'  <p>{b["text"]}</p>')
            elif b['type'] == 'voice':
                html_parts.append(f'  <div class="voice">{b["text"]}</div>')
            elif b['type'] == 'whisper':
                html_parts.append(f'  <div class="whisper">{b["text"]}</div>')
        html_parts.append('</section>')

    OUT_HTML.write_text('\n'.join(html_parts), encoding='utf-8')
    print(f"  ✓ HTML fragment saved: {OUT_HTML}")


if __name__ == '__main__':
    main()
