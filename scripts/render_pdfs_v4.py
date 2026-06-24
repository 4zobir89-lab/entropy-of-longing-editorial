#!/usr/bin/env python3
"""V4 PDF renderer — uses Chromium native page.pdf() with scrapbook elements."""
import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BUILD = Path('/home/z/my-project/build/v4')
DOWNLOAD = Path('/home/z/my-project/download')
DOWNLOAD.mkdir(parents=True, exist_ok=True)

INTERIOR_HTML = BUILD / 'book_interior_v4.html'
COVER_HTML = Path('/home/z/my-project/build/v3/book_cover_v3.html')  # reuse v3 cover

OUT_PRINT   = DOWNLOAD / 'Print_Ready_Entropy_of_Longing_FINAL.pdf'
OUT_DIGITAL = DOWNLOAD / 'Digital_Reading_Entropy_of_Longing_FINAL.pdf'
OUT_COVER   = DOWNLOAD / 'Cover_Front_Back_FINAL.pdf'
OUT_PREVIEW = DOWNLOAD / 'preview_all_pages_FINAL.jpg'


async def render_interior(page, html_path, out_path, width_mm, height_mm, override_css_page=False):
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_function("document.fonts && document.fonts.status === 'loaded'", timeout=20000)
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(1500)

    if override_css_page:
        await page.add_style_tag(content=f"@page {{ size: {width_mm}mm {height_mm}mm !important; margin: 20mm 18mm 20mm 22mm !important; }}")
        await page.wait_for_timeout(500)

    await page.pdf(
        path=str(out_path),
        width=f"{width_mm}mm",
        height=f"{height_mm}mm",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=not override_css_page,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def render_cover(page, html_path, out_path):
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_function("document.fonts && document.fonts.status === 'loaded'", timeout=20000)
    await page.wait_for_timeout(1200)
    await page.pdf(
        path=str(out_path),
        width="264mm", height="209mm",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=True,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def set_metadata(pdf_path, title, author, subject):
    try:
        from pypdf import PdfReader, PdfWriter
        r = PdfReader(str(pdf_path))
        w = PdfWriter(clone_from=r)
        w.add_metadata({
            "/Title": title, "/Author": author, "/Subject": subject,
            "/Creator": "Editorial Book Designer", "/Producer": "Playwright + pypdf",
            "/Keywords": "رواية; أدب; انتروبيا الحنين; شذى ياسر الجوبحي; اليمن; 2026",
        })
        with open(pdf_path, "wb") as f: w.write(f)
        print(f"  ✓ metadata: {pdf_path.name}")
    except Exception as e:
        print(f"  (metadata failed: {e})")


async def render_preview(print_pdf, out_path, max_pages=150):
    import tempfile
    tmpdir = Path(tempfile.mkdtemp(prefix='v4_preview_'))
    try:
        subprocess.run(['pdftoppm', '-png', '-r', '60', str(print_pdf), str(tmpdir/'page')], check=True, capture_output=True)
        from PIL import Image, ImageDraw, ImageFont
        import glob
        pngs = sorted(tmpdir.glob('page-*.png'))[:max_pages]
        if not pngs: raise RuntimeError("no PNGs")
        imgs = [Image.open(p).convert('RGB') for p in pngs]
        thumb_w = 180
        thumbs = []
        for im in imgs:
            r = thumb_w / im.width
            thumbs.append(im.resize((thumb_w, int(im.height*r)), Image.LANCZOS))
        cols = 10
        rows = (len(thumbs) + cols - 1) // cols
        gap, pad = 5, 18
        cell_w = thumb_w
        cell_h = max(t.height for t in thumbs)
        title_h = 44
        sheet_w = pad*2 + cell_w*cols + gap*(cols-1)
        sheet_h = title_h + pad + cell_h*rows + gap*(rows-1) + pad
        sheet = Image.new('RGB', (sheet_w, sheet_h), (30, 28, 26))
        draw = ImageDraw.Draw(sheet)
        arabic = glob.glob('/usr/share/fonts/**/*Noto*Naskh*.ttf', recursive=True) or glob.glob('/usr/share/fonts/**/*Amiri*.ttf', recursive=True)
        font_path = arabic[0] if arabic else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        title_font = ImageFont.truetype(font_path, 16)
        label_font = ImageFont.truetype(font_path, 8)
        draw.text((pad, 12), f'انتروبيا الحنين FINAL — {len(thumbs)} صفحة', fill=(228,201,136), font=title_font)
        for i, t in enumerate(thumbs):
            r, c = i // cols, i % cols
            x = pad + c*(cell_w+gap)
            y = title_h + pad + r*(cell_h+gap)
            sheet.paste(t, (x, y))
            draw.text((x+2, y+2), f'{i+1}', fill=(255,220,150), font=label_font)
        sheet.save(out_path, 'JPEG', quality=78, optimize=True)
        print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB, {len(thumbs)} pages)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def main():
    print('\n=== انتروبيا الحنين — V4 FINAL (with scrapbook) ===\n')
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        print('[1/4] Print-ready interior PDF (154×216 mm)...')
        page = await context.new_page()
        await render_interior(page, INTERIOR_HTML, OUT_PRINT, 154, 216)
        await set_metadata(OUT_PRINT, 'انتروبيا الحنين — النسخة النهائية للطباعة', 'شذى ياسر الجوبحي', 'رواية أدبية كاملة — 7 فصول + أقباس + ملاحق — تصميم كلاسيكي مع قصاصات بصرية')
        await page.close()

        print('\n[2/4] Digital reading PDF (A5)...')
        page = await context.new_page()
        await render_interior(page, INTERIOR_HTML, OUT_DIGITAL, 148, 210, override_css_page=True)
        await set_metadata(OUT_DIGITAL, 'انتروبيا الحنين — النسخة الرقمية النهائية', 'شذى ياسر الجوبحي', 'رواية أدبية كاملة — النسخة الرقمية A5')
        await page.close()

        print('\n[3/4] Cover spread PDF...')
        page = await context.new_page()
        await render_cover(page, COVER_HTML, OUT_COVER)
        await set_metadata(OUT_COVER, 'انتروبيا الحنين — الغلاف النهائي', 'شذى ياسر الجوبحي', 'غلاف الرواية الكامل — تصميم كلاسيكي مع قبس وخربشات')
        await page.close()

        print('\n[4/4] Preview JPG...')
        await render_preview(OUT_PRINT, OUT_PREVIEW, max_pages=150)
        await browser.close()

    # Verification
    print('\n=== Verification ===')
    try:
        from pypdf import PdfReader
        from PIL import Image
        import numpy as np
        for name in ['Print_Ready_Entropy_of_Longing_FINAL.pdf', 'Digital_Reading_Entropy_of_Longing_FINAL.pdf']:
            pp = DOWNLOAD / name
            if pp.exists():
                r = PdfReader(str(pp))
                print(f'  {name}: {len(r.pages)} pages')
        # Ink density
        tmpdir = Path('/tmp/v4_check'); tmpdir.mkdir(exist_ok=True)
        subprocess.run(['pdftoppm', '-png', '-r', '50', str(OUT_PRINT), str(tmpdir/'p')], check=True, capture_output=True)
        pngs = sorted(tmpdir.glob('p-*.png'))
        empty, low, good = [], [], 0
        for png in pngs:
            im = Image.open(png).convert('L'); arr = np.array(im)
            ink = (arr < 200).sum() / arr.size
            pg = int(png.stem.split('-')[1])
            if ink < 0.001: empty.append(pg)
            elif ink < 0.005: low.append(pg)
            else: good += 1
        print(f'  Pages: {len(pngs)} total, {good} good, {len(low)} low-ink, {len(empty)} empty')
        if empty: print(f'  Empty pages: {empty}')
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception as e:
        print(f'  (verification failed: {e})')

    print('\n=== FINAL Deliverables ===')
    for f in sorted(DOWNLOAD.glob('*FINAL*')):
        print(f'  {f.name:55s}  {f.stat().st_size/1024:>8.1f} KB')


if __name__ == '__main__':
    asyncio.run(main())
