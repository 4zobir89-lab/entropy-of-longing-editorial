#!/usr/bin/env python3
"""
V3 PDF renderer — uses Chromium native page.pdf() for reliable pagination.

This avoids Paged.js issues and uses Chromium's built-in print engine which
handles @page rules and break properties natively. We add post-processing
to verify no empty pages and proper content density.

Produces:
- Print_Ready_FULL_v3.pdf  (A5 + 3mm bleed = 154×216mm)
- Digital_Reading_FULL_v3.pdf  (A5 = 148×210mm)  
- Cover_FULL_v3.pdf  (264×209mm spread)
"""
import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BUILD = Path('/home/z/my-project/build/v3')
DOWNLOAD = Path('/home/z/my-project/download')
DOWNLOAD.mkdir(parents=True, exist_ok=True)

INTERIOR_HTML = BUILD / 'book_interior_v3.html'
COVER_HTML    = BUILD / 'book_cover_v3.html'

OUT_PRINT   = DOWNLOAD / 'Print_Ready_Entropy_of_Longing_FULL_v3.pdf'
OUT_DIGITAL = DOWNLOAD / 'Digital_Reading_Entropy_of_Longing_FULL_v3.pdf'
OUT_COVER   = DOWNLOAD / 'Cover_Front_Back_FULL_v3.pdf'
OUT_PREVIEW = DOWNLOAD / 'preview_all_pages_FULL_v3.jpg'


async def render_interior(page, html_path: Path, out_path: Path,
                          width_mm: float, height_mm: float,
                          override_css_page: bool = False):
    """Render interior HTML to PDF using Chromium native print."""
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=20000,
    )
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(1500)

    if override_css_page:
        await page.add_style_tag(content=f"""
            @page {{ size: {width_mm}mm {height_mm}mm !important; margin: 18mm 16mm 18mm 22mm !important; }}
        """)
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


async def render_cover(page, html_path: Path, out_path: Path):
    """Render cover spread — single page."""
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=20000,
    )
    await page.wait_for_timeout(1200)

    await page.pdf(
        path=str(out_path),
        width="264mm",
        height="209mm",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=True,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def set_pdf_metadata(pdf_path: Path, title: str, author: str, subject: str):
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return
    r = PdfReader(str(pdf_path))
    w = PdfWriter(clone_from=r)
    w.add_metadata({
        "/Title": title,
        "/Author": author,
        "/Subject": subject,
        "/Creator": "Editorial Book Designer · Open Design",
        "/Producer": "Playwright + pypdf",
        "/Keywords": "رواية; أدب; انتروبيا الحنين; شذى ياسر الجوبحي; اليمن; 2026",
    })
    with open(pdf_path, "wb") as f:
        w.write(f)
    print(f"  ✓ metadata stamped: {pdf_path.name}")


async def render_preview_jpg(print_pdf: Path, out_path: Path, max_pages: int = 150):
    """Render contact sheet of all pages."""
    import tempfile
    tmpdir = Path(tempfile.mkdtemp(prefix='v3_preview_'))
    try:
        subprocess.run(
            ['pdftoppm', '-png', '-r', '60', str(print_pdf), str(tmpdir / 'page')],
            check=True, capture_output=True,
        )
        from PIL import Image, ImageDraw, ImageFont
        import glob
        pngs = sorted(tmpdir.glob('page-*.png'))[:max_pages]
        if not pngs:
            raise RuntimeError("pdftoppm produced no PNGs")

        imgs = [Image.open(p).convert('RGB') for p in pngs]
        thumb_w = 180
        thumbs = []
        for im in imgs:
            ratio = thumb_w / im.width
            thumbs.append(im.resize((thumb_w, int(im.height * ratio)), Image.LANCZOS))

        cols = 10
        rows = (len(thumbs) + cols - 1) // cols
        gap = 5
        pad = 18
        cell_w = thumb_w
        cell_h = max(t.height for t in thumbs)
        title_h = 44
        sheet_w = pad*2 + cell_w*cols + gap*(cols-1)
        sheet_h = title_h + pad + cell_h*rows + gap*(rows-1) + pad
        sheet = Image.new('RGB', (sheet_w, sheet_h), (30, 28, 26))
        draw = ImageDraw.Draw(sheet)
        arabic_fonts = glob.glob('/usr/share/fonts/**/*Noto*Naskh*.ttf', recursive=True) \
                    or glob.glob('/usr/share/fonts/**/*Amiri*.ttf', recursive=True)
        font_path = arabic_fonts[0] if arabic_fonts else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        title_font = ImageFont.truetype(font_path, 16)
        label_font = ImageFont.truetype(font_path, 8)

        draw.text((pad, 12), f'انتروبيا الحنين V3 — {len(thumbs)} صفحة',
                  fill=(228, 201, 136), font=title_font)

        for i, t in enumerate(thumbs):
            r = i // cols
            c = i % cols
            x = pad + c*(cell_w+gap)
            y = title_h + pad + r*(cell_h+gap)
            sheet.paste(t, (x, y))
            draw.text((x+2, y+2), f'{i+1}', fill=(255, 220, 150), font=label_font)

        sheet.save(out_path, 'JPEG', quality=78, optimize=True)
        print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB, {len(thumbs)} pages)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def main():
    print('\n=== انتروبيا الحنين — V3 Production (Chromium native) ===\n')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # ===== 1. Print-ready interior (154×216 mm with bleed) =====
        print('[1/4] Print-ready interior PDF (154×216 mm)...')
        page = await context.new_page()
        await render_interior(page, INTERIOR_HTML, OUT_PRINT, 154, 216)
        await set_pdf_metadata(
            OUT_PRINT,
            title='انتروبيا الحنين — نسخة الطباعة V3 (الكاملة)',
            author='شذى ياسر الجوبحي',
            subject='رواية أدبية كاملة — الطبعة الأولى ٢٠٢٦ — 7 فصول + أقباس + ملاحق',
        )
        await page.close()

        # ===== 2. Digital reading PDF (A5: 148×210 mm) =====
        print('\n[2/4] Digital reading PDF (A5: 148×210 mm)...')
        page = await context.new_page()
        await render_interior(page, INTERIOR_HTML, OUT_DIGITAL, 148, 210,
                              override_css_page=True)
        await set_pdf_metadata(
            OUT_DIGITAL,
            title='انتروبيا الحنين — نسخة القراءة الرقمية V3',
            author='شذى ياسر الجوبحي',
            subject='رواية أدبية كاملة — النسخة الرقمية A5',
        )
        await page.close()

        # ===== 3. Cover spread =====
        print('\n[3/4] Cover spread PDF (264×209 mm)...')
        page = await context.new_page()
        await render_cover(page, COVER_HTML, OUT_COVER)
        await set_pdf_metadata(
            OUT_COVER,
            title='انتروبيا الحنين — الغلاف V3',
            author='شذى ياسر الجوبحي',
            subject='غلاف الرواية الكامل — تصميم كلاسيكي مع قبس وخربشات',
        )
        await page.close()

        # ===== 4. Preview JPG =====
        print('\n[4/4] Preview JPG (all pages contact sheet)...')
        await render_preview_jpg(OUT_PRINT, OUT_PREVIEW, max_pages=150)

        await browser.close()

    # Page count + ink density check
    print('\n=== Verification ===')
    try:
        from pypdf import PdfReader
        from PIL import Image
        import numpy as np

        for name in ['Print_Ready_Entropy_of_Longing_FULL_v3.pdf', 'Digital_Reading_Entropy_of_Longing_FULL_v3.pdf']:
            p = DOWNLOAD / name
            if p.exists():
                r = PdfReader(str(p))
                print(f'\n  {name}: {len(r.pages)} pages')

        # Check ink density of print PDF
        print('\n  Ink density per page (print PDF):')
        tmpdir = Path('/tmp/v3_check')
        tmpdir.mkdir(exist_ok=True)
        subprocess.run(
            ['pdftoppm', '-png', '-r', '50', str(OUT_PRINT), str(tmpdir / 'p')],
            check=True, capture_output=True,
        )
        pngs = sorted(tmpdir.glob('p-*.png'))
        low_ink = 0
        empty = 0
        for png in pngs:
            im = Image.open(png).convert('L')
            arr = np.array(im)
            ink = (arr < 200).sum() / arr.size
            pg = int(png.stem.split('-')[1])
            if ink < 0.001:
                empty += 1
                print(f'    p{pg:02d}: EMPTY ⚠')
            elif ink < 0.005:
                low_ink += 1
        if empty == 0 and low_ink <= 5:
            print(f'    ✓ All pages have content (low-ink pages: {low_ink})')
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception as e:
        print(f'  (verification failed: {e})')

    # Final summary
    print('\n=== V3 Deliverables ===')
    for f in sorted(DOWNLOAD.glob('*_v3.*')):
        print(f'  {f.name:55s}  {f.stat().st_size/1024:>8.1f} KB')


if __name__ == '__main__':
    asyncio.run(main())
