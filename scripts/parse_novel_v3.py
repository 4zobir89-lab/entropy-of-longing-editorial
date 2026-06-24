#!/usr/bin/env python3
"""
V3 parser — انتروبيا الحنين
Produces book-data-v3.json with:
- Dialogue splitting: every speaker in their own paragraph
- Qibas linked after each chapter (qubus[chapter_idx])
- Appendices at the end (ملحقات + أقباس)
- Classic literary structure
"""
import json
import re
from pathlib import Path

SRC = Path('/tmp/novel_clean.md')
OUT = Path('/home/z/my-project/build/v3/book-data-v3.json')


def clean_text(t: str) -> str:
    t = re.sub(r'\\`', '', t)
    t = re.sub(r'`', '', t)
    t = re.sub(r'^\[\]\s*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\[\]', '', t)
    t = re.sub(r'^\s*#\*\*[^*]*\*\*\s*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\*\*\*-\s*([^*]+?)\*\*\*', r'- \1', t)
    t = '\n'.join(line.rstrip() for line in t.split('\n'))
    return t.strip()


def split_dialogue(text: str) -> list:
    """Split a paragraph into dialogue segments.
    
    Arabic dialogue uses " or « ». When speaker changes, start a new paragraph.
    Returns list of blocks: {type: 'voice'|'p', text: ...}
    """
    text = text.strip()
    if not text:
        return []
    
    # If no quotes at all, return as single narration
    if '"' not in text and '«' not in text:
        return [{'type': 'p', 'text': text}]
    
    # Use " as primary quote marker (most common in the source)
    # Split keeping the quote chars
    parts = re.split(r'(")', text)
    
    blocks = []
    current_narration = ''
    current_quote = ''
    in_quote = False
    
    for part in parts:
        if part == '"':
            if in_quote:
                # Closing quote — finalize the quote block
                current_quote += part
                # Emit narration before this quote (if any)
                if current_narration.strip():
                    blocks.append({'type': 'p', 'text': current_narration.strip()})
                    current_narration = ''
                # Emit the quote as voice
                blocks.append({'type': 'voice', 'text': current_quote.strip()})
                current_quote = ''
                in_quote = False
            else:
                # Opening quote — emit narration before it
                if current_narration.strip():
                    blocks.append({'type': 'p', 'text': current_narration.strip()})
                    current_narration = ''
                current_quote = part
                in_quote = True
        else:
            if in_quote:
                current_quote += part
            else:
                current_narration += part
    
    # Trailing narration
    if current_narration.strip():
        blocks.append({'type': 'p', 'text': current_narration.strip()})
    # Trailing unclosed quote (shouldn't happen but safe)
    if current_quote.strip():
        blocks.append({'type': 'voice', 'text': current_quote.strip()})
    
    # Merge consecutive p blocks (narration fragments between quotes that are tiny)
    merged = []
    for b in blocks:
        if b['type'] == 'p' and merged and merged[-1]['type'] == 'p':
            # Merge if both are short narration fragments
            if len(merged[-1]['text']) < 80 and len(b['text']) < 80:
                merged[-1]['text'] += ' ' + b['text']
            else:
                merged.append(b)
        else:
            merged.append(b)
    
    return merged


def parse_paragraph_to_blocks(para: str) -> list:
    para = clean_text(para)
    if not para:
        return []
    
    stripped = para.strip()
    
    # Skip stray hashtag lines
    if re.match(r'^\*{0,2}#\S+\*{0,2}$', stripped):
        return []
    
    # Signature line
    if re.match(r'^-\s*شذى', stripped):
        return [{'type': 'signature', 'text': stripped}]
    
    # Pure italic whisper (starts and ends with *, not **)
    if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
        inner = stripped.strip('*').strip()
        if inner:
            return [{'type': 'whisper', 'text': inner}]
    
    # Split dialogues within the paragraph
    return split_dialogue(stripped)


def split_paragraphs(text: str) -> list:
    paras = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paras if p.strip()]


def parse_chapter(title: str, body: str) -> dict:
    m = re.match(r'الفصل\s+([^:]+):\s*(.+)', title)
    if m:
        chapter_ord = m.group(1).strip()
        chapter_title = m.group(2).strip()
    else:
        chapter_ord = ''
        chapter_title = title
    
    epigraph = None
    blocks = []
    paras = split_paragraphs(body)
    
    for i, para in enumerate(paras):
        if not para.strip():
            continue
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


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    content = clean_text(SRC.read_text(encoding='utf-8'))
    
    # Normalize H1 أقباس to H2
    content = re.sub(
        r'\n#\s+\*\*أقباس وملاحق الرواية\*\*\s*\n',
        '\n## **أقباس وملاحق الرواية**\n',
        content
    )
    
    parts = re.split(r'\n##\s+\*\*([^*]+)\*\*\s*\n', content)
    preamble = parts[0]
    sections_raw = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i+1] if i+1 < len(parts) else ''
        sections_raw.append((title, body))
    
    # Parse preamble
    dedication = None
    preface = None
    preface_epigraph = None
    
    h1_parts = re.split(r'\n#\s+\*\*([^*]+)\*\*\s*\n', preamble)
    
    for i in range(1, len(h1_parts), 2):
        h1_title = h1_parts[i].strip()
        h1_body = h1_parts[i+1] if i+1 < len(h1_parts) else ''
        if 'إهداء' in h1_title:
            ded_paras = split_paragraphs(h1_body)
            ded_lines = []
            for p in ded_paras:
                p_clean = clean_text(p)
                if p_clean:
                    p_clean = re.sub(r'#\S+', '', p_clean).strip()
                    p_clean = re.sub(r'^\*\*|\*\*$', '', p_clean).strip()
                    if p_clean:
                        ded_lines.append(p_clean)
            dedication = {'lines': ded_lines}
        elif 'مقدمة' in h1_title:
            pre_paras = split_paragraphs(h1_body)
            preface_blocks = []
            for j, p in enumerate(pre_paras):
                p_clean = clean_text(p)
                if not p_clean:
                    continue
                if j < 3 and ('لا شيء يُفنى' in p_clean or 'لا شيء يفنى' in p_clean):
                    ep = p_clean.strip('*').strip().strip('"').strip()
                    preface_epigraph = ep
                    continue
                preface_blocks.extend(parse_paragraph_to_blocks(p))
            preface = {'epigraph': preface_epigraph, 'blocks': preface_blocks}
    
    # Parse chapters + appendices + qibas
    chapters = []
    appendices = []
    qibas_list = []  # 7 qibas
    
    for title, body in sections_raw:
        if title.startswith('الفصل'):
            cut_match = re.search(r'\n###\s+\*\*قُبس', body)
            if cut_match:
                body = body[:cut_match.start()]
            chapters.append(parse_chapter(title, body))
        elif 'أقباس وملاحق' in title:
            # Parse the 7 qibas
            sub_parts = re.split(r'\n###\s+\*\*([^*]+)\*\*\s*\n', body)
            intro = sub_parts[0].strip()
            # The intro may contain قُبس أول embedded as heading
            if intro:
                intro_blocks = []
                for para in split_paragraphs(intro):
                    p_clean = clean_text(para)
                    if not p_clean:
                        continue
                    heading_match = re.match(r'^###\s+\*\*([^*]+)\*\*\s*$', p_clean)
                    if heading_match:
                        # Start a new qibas entry
                        qibas_list.append({
                            'title': heading_match.group(1).strip(),
                            'blocks': []
                        })
                    else:
                        if qibas_list:
                            qibas_list[-1]['blocks'].extend(parse_paragraph_to_blocks(p_clean))
                        else:
                            intro_blocks.extend(parse_paragraph_to_blocks(p_clean))
            for j in range(1, len(sub_parts), 2):
                sub_title = sub_parts[j].strip()
                sub_body = sub_parts[j+1] if j+1 < len(sub_parts) else ''
                sub_blocks = []
                for para in split_paragraphs(sub_body):
                    sub_blocks.extend(parse_paragraph_to_blocks(para))
                qibas_list.append({'title': sub_title, 'blocks': sub_blocks})
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
    
    # Link each qibas to its chapter (qibas 1 → chapter 1, etc.)
    # The qibas are already in order: قُبس أول، قُبس ثاني، ... القُبس السابع
    # Chapters are also 7 in order
    for i, ch in enumerate(chapters):
        if i < len(qibas_list):
            ch['qibas'] = qibas_list[i]
        else:
            ch['qibas'] = None
    
    # The last qibas (القُبس الأخير) stays in the appendices
    # Already handled above (it's in appendices[1].sub_sections[0])
    
    book = {
        'title': 'انتروبيا الحنين',
        'subtitle': 'رواية',
        'author': 'شذى ياسر الجوبحي',
        'author_short': 'شذى ياسر',
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
        if ch.get('qibas'):
            total_blocks += len(ch['qibas']['blocks'])
    for ap in appendices:
        if ap['intro']:
            total_blocks += len(ap['intro'])
        for ss in ap['sub_sections']:
            total_blocks += len(ss['blocks'])
    
    print(f"=== V3 Book parsed ===")
    print(f"  Title: {book['title']}")
    print(f"  Author: {book['author']}")
    print(f"  Dedication lines: {len(dedication['lines']) if dedication else 0}")
    print(f"  Preface blocks: {len(preface['blocks']) if preface else 0}")
    print(f"  Chapters: {len(chapters)}")
    for i, ch in enumerate(chapters):
        qibas_info = f" + qibas: {ch['qibas']['title']}" if ch.get('qibas') else ""
        print(f"    {ch['num']:15s} | {ch['title'][:40]:40s} | {len(ch['blocks'])} blocks{qibas_info}")
    print(f"  Appendices: {len(appendices)}")
    for ap in appendices:
        ss_count = len(ap['sub_sections'])
        print(f"    {ap['title'][:50]:50s} | {ss_count} sub-sections")
    print(f"  Total text blocks (with dialogue splitting): {total_blocks}")
    
    OUT.write_text(json.dumps(book, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n  ✓ JSON saved: {OUT}")


if __name__ == '__main__':
    main()
