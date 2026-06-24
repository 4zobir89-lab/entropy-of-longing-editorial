#!/usr/bin/env python3
"""
Generate professional-quality PDFs for انتروبيا الحنين (full novel).

Produces 3 PDFs:
1. Print_Ready_Entropy_of_Longing_FULL.pdf  — 6×9 inch + 3mm bleed (158×235mm)
2. Digital_Reading_Entropy_of_Longing_FULL.pdf  — A5 (148×210mm)
3. Cover_Front_Back_FULL.pdf  — full cover spread (back + spine + front, 318×235mm)

Uses Playwright (Chromium) with page.pdf() for vector-quality output.
Fonts are loaded from Google Fonts CDN and embedded in the PDF.
"""
import asyncio
import os
import shutil
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BUILD = Path('/home/z/my-project/build/v2')
DOWNLOAD = Path('/home/z/my-project/download')
DOWNLOAD.mkdir(parents=True, exist_ok=True)

INTERIOR_PRINT_HTML   = BUILD / 'book_interior_full.html'
INTERIOR_DIGITAL_HTML = BUILD / 'book_interior_digital.html'
COVER_HTML            = BUILD / 'book_cover_full.html'  # We'll build this next

OUT_PRINT     = DOWNLOAD / 'Print_Ready_Entropy_of_Longing_FULL.pdf'
OUT_DIGITAL   = DOWNLOAD / 'Digital_Reading_Entropy_of_Longing_FULL.pdf'
OUT_COVER     = DOWNLOAD / 'Cover_Front_Back_FULL.pdf'
OUT_PREVIEW   = DOWNLOAD / 'preview_all_pages_FULL.jpg'


async def render_pdf(page, html_path: Path, out_path: Path,
                     width_mm: float, height_mm: float,
                     override_css_page: bool = False):
    """Render an HTML file to a multi-page PDF at the given trim size."""
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    # Wait for fonts to load
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=20000,
    )
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(1000)

    if override_css_page:
        # Override the @page rule and all .page heights
        await page.add_style_tag(content=f"""
            @page {{ size: {width_mm}mm {height_mm}mm !important; margin: 0 !important; }}
            .page {{ width: {width_mm}mm !important; height: {height_mm}mm !important; min-height: {height_mm}mm !important; }}
            .chapter-opener-page, .appendix-opener-page {{ height: {height_mm}mm !important; min-height: {height_mm}mm !important; }}
            .dedication-page {{ height: {height_mm}mm !important; min-height: {height_mm}mm !important; }}
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
    """Render the cover spread — single-page PDF."""
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until='networkidle')
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=20000,
    )
    await page.wait_for_timeout(1000)

    await page.pdf(
        path=str(out_path),
        width="318mm",
        height="235mm",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=True,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def set_pdf_metadata(pdf_path: Path, title: str, author: str, subject: str):
    """Stamp PDF metadata."""
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


async def render_preview_jpg(print_pdf: Path, out_path: Path, max_pages: int = 60):
    """Render a contact sheet JPG of all pages."""
    import tempfile
    tmpdir = Path(tempfile.mkdtemp(prefix='book_preview_'))
    try:
        # pdftoppm → PNG at 90 DPI
        png_prefix = tmpdir / 'page'
        subprocess.run(
            ['pdftoppm', '-png', '-r', '90', str(print_pdf), str(png_prefix)],
            check=True, capture_output=True,
        )

        from PIL import Image, ImageDraw, ImageFont
        pngs = sorted(tmpdir.glob('page-*.png'))[:max_pages]
        if not pngs:
            raise RuntimeError("pdftoppm produced no PNGs")

        imgs = [Image.open(p).convert('RGB') for p in pngs]
        # Resize all to uniform thumbnail
        thumb_w = 280
        thumbs = []
        for im in imgs:
            ratio = thumb_w / im.width
            thumbs.append(im.resize((thumb_w, int(im.height * ratio)), Image.LANCZOS))

        # Layout: 8 columns
        cols = 8
        rows = (len(thumbs) + cols - 1) // cols
        gap = 8
        pad = 24
        cell_w = thumb_w
        cell_h = max(t.height for t in thumbs)
        title_h = 60
        sheet_w = pad*2 + cell_w*cols + gap*(cols-1)
        sheet_h = title_h + pad + cell_h*rows + gap*(rows-1) + pad
        sheet = Image.new('RGB', (sheet_w, sheet_h), (30, 28, 26))
        draw = ImageDraw.Draw(sheet)
        try:
            # Find Arabic-capable font
            import glob
            arabic_fonts = glob.glob('/usr/share/fonts/**/*Noto*Naskh*.ttf', recursive=True) \
                        or glob.glob('/usr/share/fonts/**/*Amiri*.ttf', recursive=True) \
                        or glob.glob('/usr/share/fonts/**/*Plex*Arabic*.ttf', recursive=True)
            font_path = arabic_fonts[0] if arabic_fonts else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
            title_font = ImageFont.truetype(font_path, 22)
            label_font = ImageFont.truetype(font_path, 11)
        except Exception:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        draw.text((pad, 16), f'انتروبيا الحنين — معاينة شاملة ({len(thumbs)} صفحة)',
                  fill=(228, 201, 136), font=title_font)

        for i, t in enumerate(thumbs):
            r = i // cols
            c = i % cols
            x = pad + c*(cell_w+gap)
            y = title_h + pad + r*(cell_h+gap)
            sheet.paste(t, (x, y))
            draw.text((x+4, y+4), f'p{i+1:02d}', fill=(255, 220, 150), font=label_font)

        sheet.save(out_path, 'JPEG', quality=82, optimize=True)
        print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB, {len(thumbs)} pages)")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def main():
    print('\n=== انتروبيا الحنين — FULL NOVEL Production Pipeline ===\n')

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # ===== 1. Print-ready interior (158×235 mm with bleed) =====
        print('[1/4] Print-ready interior PDF (158×235 mm with bleed)...')
        page = await context.new_page()
        await render_pdf(page, INTERIOR_PRINT_HTML, OUT_PRINT, 158, 235)
        await set_pdf_metadata(
            OUT_PRINT,
            title='انتروبيا الحنين — نسخة الطباعة (الكاملة)',
            author='شذى ياسر الجوبحي',
            subject='رواية أدبية / فلسفية / نفسية — الطبعة الأولى ٢٠٢٦ — 7 فصول + ملاحق',
        )
        await page.close()

        # ===== 2. Digital reading PDF (A5) =====
        print('\n[2/4] Digital reading PDF (A5: 148×210 mm)...')
        page = await context.new_page()
        await render_pdf(page, INTERIOR_DIGITAL_HTML, OUT_DIGITAL, 148, 210,
                         override_css_page=True)
        await set_pdf_metadata(
            OUT_DIGITAL,
            title='انتروبيا الحنين — نسخة القراءة الرقمية (الكاملة)',
            author='شذى ياسر الجوبحي',
            subject='رواية أدبية — النسخة الرقمية A5',
        )
        await page.close()

        # ===== 3. Cover spread =====
        if COVER_HTML.exists():
            print('\n[3/4] Cover spread PDF (318×235 mm with bleed)...')
            page = await context.new_page()
            await render_cover(page, COVER_HTML, OUT_COVER)
            await set_pdf_metadata(
                OUT_COVER,
                title='انتروبيا الحنين — الغلاف',
                author='شذى ياسر الجوبحي',
                subject='غلاف الرواية الكامل (خلفي + كعب + أمامي)',
            )
            await page.close()
        else:
            print(f'\n[3/4] Cover HTML not found at {COVER_HTML}, skipping cover.')

        # ===== 4. Preview JPG =====
        print('\n[4/4] Preview JPG (all pages contact sheet)...')
        await render_preview_jpg(OUT_PRINT, OUT_PREVIEW, max_pages=60)

        await browser.close()

    # Print summary
    print('\n=== Deliverables ===')
    for f in sorted(DOWNLOAD.glob('*.pdf')):
        print(f'  {f.name:55s}  {f.stat().st_size/1024:>8.1f} KB')
    for f in sorted(DOWNLOAD.glob('*.jpg')):
        print(f'  {f.name:55s}  {f.stat().st_size/1024:>8.1f} KB')


if __name__ == '__main__':
    asyncio.run(main())
