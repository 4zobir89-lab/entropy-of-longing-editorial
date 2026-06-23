#!/usr/bin/env python3
"""
انتروبيا الحنين — Book production pipeline.

Generates:
  1. Print_Ready_Entropy_of_Longing.pdf  — 6×9 inch + 3mm bleed, full interior
  2. Digital_Reading_Entropy_of_Longing.pdf  — A5, internal TOC links
  3. Cover_Front_Back.pdf  — back + spine + front spread (with bleed)
  4. preview_first_10_pages.jpg  — first 10 interior pages as a JPG contact sheet

The HTML sources live in /home/z/my-project/build/:
  - book_interior.html
  - book_cover.html

We use Playwright (Chromium) to render each HTML to PDF with page.pdf().
"""

import asyncio
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright

BUILD = Path("/home/z/my-project/build")
DOWNLOAD = Path("/home/z/my-project/download")
DOWNLOAD.mkdir(parents=True, exist_ok=True)

INTERIOR_HTML = BUILD / "book_interior.html"
COVER_HTML    = BUILD / "book_cover.html"

OUT_PRINT     = DOWNLOAD / "Print_Ready_Entropy_of_Longing.pdf"
OUT_DIGITAL   = DOWNLOAD / "Digital_Reading_Entropy_of_Longing.pdf"
OUT_COVER     = DOWNLOAD / "Cover_Front_Back.pdf"
OUT_PREVIEW   = DOWNLOAD / "preview_first_10_pages.jpg"


async def render_pdf(page, html_path: Path, out_path: Path,
                     width_mm: float, height_mm: float,
                     print_background: bool = True,
                     override_css_page: bool = False):
    """Render an HTML file to a multi-page PDF at the given trim size.

    If override_css_page=True, we inject an inline <style> override so that
    Chromium's @page rule matches the requested size (used for the digital
    A5 version where we want a different size than the print version).
    """
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=15000,
    )
    await page.evaluate("document.fonts.ready")
    await page.wait_for_timeout(800)

    if override_css_page:
        # Override the @page rule and all .page / .page-chapter-opener heights
        await page.add_style_tag(content=f"""
            @page {{ size: {width_mm}mm {height_mm}mm !important; margin: 0 !important; }}
            .page {{ width: {width_mm}mm !important; height: {height_mm}mm !important; min-height: {height_mm}mm !important; }}
            .page-chapter-opener {{ height: {height_mm}mm !important; min-height: {height_mm}mm !important; }}
        """)
        await page.wait_for_timeout(400)

    await page.pdf(
        path=str(out_path),
        width=f"{width_mm}mm",
        height=f"{height_mm}mm",
        print_background=print_background,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=not override_css_page,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def render_cover(page, html_path: Path, out_path: Path):
    """Render the cover spread — single-page PDF at 318×235mm."""
    url = html_path.resolve().as_uri()
    await page.goto(url, wait_until="networkidle")
    await page.wait_for_function(
        "document.fonts && document.fonts.status === 'loaded'",
        timeout=15000,
    )
    await page.wait_for_timeout(800)

    await page.pdf(
        path=str(out_path),
        width="318mm",
        height="235mm",
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
        prefer_css_page_size=True,
    )
    print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB)")


async def render_preview_jpg(page, html_path: Path, out_path: Path,
                              num_pages: int = 10):
    """Render the first N interior pages as a contact-sheet JPG.

    Approach: render the interior HTML to a temp PDF, rasterize each page to
    PNG via pdftoppm, then montage them into a single JPG via Pillow.
    """
    import tempfile
    tmpdir = Path(tempfile.mkdtemp(prefix="book_preview_"))
    try:
        # 1. Render interior to PDF (same as print but in tmp)
        tmp_pdf = tmpdir / "interior.pdf"
        await render_pdf(page, html_path, tmp_pdf, width_mm=158, height_mm=235)

        # 2. pdftoppm → PNG at 110 DPI
        png_prefix = tmpdir / "page"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "110", "-l", str(num_pages),
             str(tmp_pdf), str(png_prefix)],
            check=True, capture_output=True,
        )

        # 3. Montage with Pillow
        from PIL import Image
        pngs = sorted(tmpdir.glob("page-*.png"))[:num_pages]
        if not pngs:
            raise RuntimeError("pdftoppm produced no PNGs")
        imgs = [Image.open(p).convert("RGB") for p in pngs]

        # Layout: 2 columns × 5 rows (for 10 pages) — gives a tidy contact sheet
        cols = 2
        rows = (len(imgs) + cols - 1) // cols
        gap = 18
        pad = 40
        bg = (42, 40, 38)  # warm dark
        label_color = (244, 241, 234)

        # Resize all to a uniform thumbnail width
        thumb_w = 520
        thumbs = []
        for im in imgs:
            ratio = thumb_w / im.width
            thumbs.append(im.resize((thumb_w, int(im.height * ratio)), Image.LANCZOS))

        cell_w = thumb_w
        cell_h = max(t.height for t in thumbs)
        sheet_w = pad * 2 + cell_w * cols + gap * (cols - 1)
        sheet_h = pad * 2 + cell_h * rows + gap * (rows - 1) + 60  # extra for title

        sheet = Image.new("RGB", (sheet_w, sheet_h), bg)

        # Title bar
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(sheet)
        try:
            # Look for any installed Arabic-capable font
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
            # Find Arabic font
            import glob
            arabic_fonts = glob.glob("/usr/share/fonts/**/*Noto*Naskh*.ttf", recursive=True) \
                        or glob.glob("/usr/share/fonts/**/*Amiri*.ttf", recursive=True) \
                        or glob.glob("/usr/share/fonts/**/*Plex*Arabic*.ttf", recursive=True)
            if arabic_fonts:
                font_paths.insert(0, arabic_fonts[0])
            title_font = ImageFont.truetype(font_paths[0], 28)
            sub_font   = ImageFont.truetype(font_paths[0], 14)
        except Exception:
            title_font = ImageFont.load_default()
            sub_font   = ImageFont.load_default()

        title_text = "انتروبيا الحنين — معاينة أول ١٠ صفحات"
        sub_text   = "شذى ياسر الجوبحي · الطبعة الأولى ٢٠٢٦"
        draw.text((pad, 12), title_text, fill=label_color, font=title_font)
        draw.text((pad, 44), sub_text, fill=(184, 153, 104), font=sub_font)

        # Paste thumbnails
        for i, t in enumerate(thumbs):
            r = i // cols
            c = i % cols
            x = pad + c * (cell_w + gap)
            y = pad + 60 + r * (cell_h + gap)
            sheet.paste(t, (x, y))

        sheet.save(out_path, "JPEG", quality=88, optimize=True)
        print(f"  ✓ {out_path.name}  ({out_path.stat().st_size/1024:.1f} KB, {len(thumbs)} pages)")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def set_pdf_metadata(pdf_path: Path, title: str, author: str, subject: str):
    """Stamp PDF metadata (Title/Author/Subject/Creator) using pypdf."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print(f"  (skip metadata for {pdf_path.name}: pypdf not installed)")
        return
    r = PdfReader(str(pdf_path))
    w = PdfWriter(clone_from=r)
    w.add_metadata({
        "/Title": title,
        "/Author": author,
        "/Subject": subject,
        "/Creator": "Open Design · Editorial Book Designer",
        "/Producer": "Playwright + pypdf",
        "/Keywords": "رواية; أدب; انتروبيا الحنين; شذى ياسر الجوبحي; اليمن",
    })
    with open(pdf_path, "wb") as f:
        w.write(f)
    print(f"  ✓ metadata stamped: {pdf_path.name}")


async def main():
    print("\n=== انتروبيا الحنين — Book Production Pipeline ===\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # ----- Print-ready interior (6×9 inch + 3mm bleed = 158×235 mm) -----
        print("[1/4] Print-ready interior PDF (158×235 mm with bleed)...")
        page = await context.new_page()
        await render_pdf(page, INTERIOR_HTML, OUT_PRINT, 158, 235)
        await set_pdf_metadata(
            OUT_PRINT,
            title="انتروبيا الحنين — نسخة الطباعة",
            author="شذى ياسر الجوبحي",
            subject="رواية أدبية / فلسفية / نفسية — الطبعة الأولى ٢٠٢٦",
        )
        await page.close()

        # ----- Digital reading PDF (A5: 148×210 mm) -----
        # We re-render the SAME interior HTML but at A5 page size, overriding
        # the print-oriented @page rule via injected CSS. Internal TOC links
        # are already <a href="#chapter-N"> which Playwright preserves as
        # PDF link annotations.
        print("\n[2/4] Digital reading PDF (A5: 148×210 mm)...")
        page = await context.new_page()
        await render_pdf(page, INTERIOR_HTML, OUT_DIGITAL, 148, 210,
                         override_css_page=True)
        await set_pdf_metadata(
            OUT_DIGITAL,
            title="انتروبيا الحنين — نسخة القراءة الرقمية",
            author="شذى ياسر الجوبحي",
            subject="رواية أدبية — النسخة الرقمية A5",
        )
        await page.close()

        # ----- Cover spread (back + spine + front, 318×235 mm with bleed) -----
        print("\n[3/4] Cover spread PDF (318×235 mm with bleed)...")
        page = await context.new_page()
        await render_cover(page, COVER_HTML, OUT_COVER)
        await set_pdf_metadata(
            OUT_COVER,
            title="انتروبيا الحنين — الغلاف",
            author="شذى ياسر الجوبحي",
            subject="غلاف الرواية (خلفي + كعب + أمامي)",
        )
        await page.close()

        # ----- Preview JPG (first 10 pages contact sheet) -----
        print("\n[4/4] Preview JPG (first 10 interior pages)...")
        page = await context.new_page()
        await render_preview_jpg(page, INTERIOR_HTML, OUT_PREVIEW, num_pages=10)
        await page.close()

        await browser.close()

    # ----- Copy HTML sources + fonts reference into download/ -----
    print("\n[5/5] Packaging HTML sources & fonts reference...")
    src_dir = DOWNLOAD / "source_html"
    src_dir.mkdir(exist_ok=True)
    shutil.copy(INTERIOR_HTML, src_dir / "book_interior.html")
    shutil.copy(COVER_HTML,    src_dir / "book_cover.html")

    fonts_dir = DOWNLOAD / "Fonts"
    fonts_dir.mkdir(exist_ok=True)
    fonts_readme = fonts_dir / "FONTS_README.txt"
    fonts_readme.write_text(
        "انتروبيا الحنين — مرجع الخطوط\n"
        "================================\n\n"
        "الخطوط المستخدمة في الإخراج (كلها مجانية من Google Fonts):\n\n"
        "1. IBM Plex Sans Arabic (SemiBold 600, Regular 400, Light 300)\n"
        "   — للعناوين والهوامش وأرقام الصفحات\n"
        "   رخصة: SIL Open Font License 1.1\n"
        "   المصدر: https://fonts.google.com/specimen/IBM+Plex+Sans+Arabic\n\n"
        "2. Noto Naskh Arabic (Regular 400, Bold 700)\n"
        "   — لمتن الرواية والنص الأساسي\n"
        "   رخصة: SIL Open Font License 1.1\n"
        "   المصدر: https://fonts.google.com/specimen/Noto+Naskh+Arabic\n\n"
        "3. Reem Kufi (Regular 400, Medium 500)\n"
        "   — للعناوين الكبرى وأرقام الفصول على الغلاف\n"
        "   رخصة: SIL Open Font License 1.1\n"
        "   المصدر: https://fonts.google.com/specimen/Reem+Kufi\n\n"
        "4. Amiri (Regular Italic 400, Bold 700) — خط ثانوي للاقتباسات\n"
        "   رخصة: SIL Open Font License 1.1\n"
        "   المصدر: https://fonts.google.com/specimen/Amiri\n\n"
        "كل الخطوط مضمّنة في ملف PDF عبر @font-face من Google Fonts CDN\n"
        "أثناء التصدير، لذا لا تحتاج لتثبيتها محليًا لعرض الملف.\n\n"
        "للطباعة: تأكد من تضمين الخطوط (Embed All Fonts) في إعدادات\n"
        "المطبعة عند إرسال ملف PDF/X-4.\n",
        encoding="utf-8",
    )

    print("\n=== All deliverables ready ===")
    for f in sorted(DOWNLOAD.iterdir()):
        if f.is_file():
            print(f"  {f.name:55s}  {f.stat().st_size/1024:>8.1f} KB")
        elif f.is_dir():
            print(f"  {f.name}/")


if __name__ == "__main__":
    asyncio.run(main())
