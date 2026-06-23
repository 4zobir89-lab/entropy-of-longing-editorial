# انتروبيا الحنين — ملفات الإخراج النهائية

**رواية · شذى ياسر الجوبحي · الطبعة الأولى ٢٠٢٦**

---

## الملفات المُسلّمة

| الملف | الوصف | المواصفات |
|---|---|---|
| `Print_Ready_Entropy_of_Longing.pdf` | نسخة الطباعة | 6×9 inch (152×229mm) + bleed 3mm = 158×235mm · 24 صفحة |
| `Digital_Reading_Entropy_of_Longing.pdf` | نسخة القراءة الرقمية | A5 (148×210mm) · 26 صفحة · روابط فهرس داخلية |
| `Cover_Front_Back.pdf` | الغلاف الكامل | خلفي + كعب + أمامي · 318×235mm + bleed |
| `preview_first_10_pages.jpg` | معاينة أول 10 صفحات | لقطات سريعة للهوية البصرية |
| `preview_all_pages.jpg` | معاينة شاملة | الغلاف + كل الصفحات الداخلية |
| `source_html/` | المصدر القابل للتعديل | `book_interior.html` + `book_cover.html` |
| `Fonts/FONTS_README.txt` | مرجع الخطوط | IBM Plex Sans Arabic · Noto Naskh · Reem Kufi · Amiri |

---

## الهوية البصرية

- **اللوحة اللونية**: parchment cream `#F4F1EA` + warm ink `#1B1A17` + faded brass `#8C6B3F` + deep night `#0E1116`
- **الخطوط**: IBM Plex Sans Arabic SemiBold (عناوين) · Noto Naskh Arabic (متن) · Reem Kufi (عرض الغلاف) · Amiri (اقتباسات)
- **الاتجاه**: Literary Editorial + Quiet Luxury + Cosmic Nostalgia

## بنية الكتاب

1. صفحة فارغة (flyleaf)
2. صفحة العنوان
3. صفحة حقوق النشر (بها رقم الهاتف +967 775 863 594)
4. الإهداء (تصميم شاعري منفصل)
5. المقدمة (اقتباس البداية + توقيع)
6. الفهرس (بروابط داخلية للنسخة الرقمية)
7. الفصل الأول: الكف التي لا تتحلل
8. الفصل الثاني: الخط ٤٤ — حيث لم أُولد
9. الفصل الثالث: الخط ١٢ — المعادلة المعكوسة

كل فصل يبدأ بصفحة منفصلة: رقم ضخم شبحي 240pt + مدار SVG + اقتباس افتتاحي.

## للتعديل لاحقاً

- عدّل `source_html/book_interior.html` أو `source_html/book_cover.html`
- أعد التشغيل: `python3 /home/z/my-project/scripts/build_book.py`

## ملاحظات للطباعة

- ملف PDF الطباعة بحجم 158×235mm (شامل الـ bleed 3mm لكل جهة)
- للإنتاج الفعلي بـ CMYK + PDF/X-4: افتح الملف في Adobe Acrobat أو Affinity Publisher وحوّل ملف RGB → CMYK باستخدام profile ISO Coated v2 (ECI)
- الخطوط مضمّنة في الـ PDF (subset embedding عبر Chromium)
