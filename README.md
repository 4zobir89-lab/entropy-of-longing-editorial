# انتروبيا الحنين

> رواية أدبية / فلسفية / نفسية لـ **شذى ياسر الجوبحي** · الطبعة الأولى ٢٠٢٦

رواية عن الحنين، الفيزياء، والأكوان المتعددة. تبحث الابنة عن أبيها الفيزيائي في كل خطٍّ من خطوط دفتره الأزرق — كونٌ حيث لم يمت، وآخر حيث لم تُولد، وثالثٌ حيث صار هو الطفل وهي الأم.

---

## المُسلّمات

| الملف | الوصف |
|---|---|
| [`Print_Ready_Entropy_of_Longing.pdf`](public/Print_Ready_Entropy_of_Longing.pdf) | نسخة الطباعة · 6×9 inch + bleed 3mm · 24 صفحة |
| [`Digital_Reading_Entropy_of_Longing.pdf`](public/Digital_Reading_Entropy_of_Longing.pdf) | نسخة القراءة الرقمية · A5 · 26 صفحة · روابط فهرس داخلية |
| [`Cover_Front_Back.pdf`](public/Cover_Front_Back.pdf) | الغلاف الكامل · خلفي + كعب + أمامي + bleed |
| [`preview_all_pages.jpg`](public/preview_all_pages.jpg) | معاينة شاملة: الغلاف + كل الصفحات |
| [`preview_first_10_pages.jpg`](public/preview_first_10_pages.jpg) | معاينة أول 10 صفحات |
| [`source_html/`](public/source_html/) | القوالب المصدرية القابلة للتعديل |

---

## الهوية البصرية

- **اللوحة اللونية**: parchment cream `#F4F1EA` + warm ink `#1B1A17` + faded brass `#8C6B3F` + deep night `#0E1116`
- **الخطوط**: IBM Plex Sans Arabic SemiBold (عناوين) · Noto Naskh Arabic (متن) · Reem Kufi (عرض الغلاف وأرقام الفصول الشبحية 240pt) · Amiri (اقتباسات)
- **الاتجاه**: Literary Editorial + Quiet Luxury + Cosmic Nostalgia

---

## بنية الكتاب

1. صفحة فارغة (flyleaf)
2. صفحة العنوان
3. صفحة حقوق النشر
4. الإهداء (تصميم شاعري منفصل)
5. المقدمة (اقتباس البداية + توقيع)
6. الفهرس (بروابط داخلية للنسخة الرقمية)
7. الفصل الأول: الكف التي لا تتحلل
8. الفصل الثاني: الخط ٤٤ — حيث لم أُولد
9. الفصل الثالث: الخط ١٢ — المعادلة المعكوسة

كل فصل يبدأ بصفحة منفصلة: رقم ضخم شبحي 240pt + مدار SVG + اقتباس افتتاحي.

---

## للتعديل وإعادة الإنتاج

```bash
# 1. عدّل القالب
vim public/source_html/book_interior.html

# 2. أعد التوليد
python3 scripts/build_book.py
```

## للطباعة الفعلية

ملف PDF الطباعة بحجم 158×235mm (شامل الـ bleed 3mm لكل جهة). للإنتاج الفعلي بـ CMYK + PDF/X-4: افتح الملف في Adobe Acrobat أو Affinity Publisher وحوّل RGB → CMYK باستخدام profile ISO Coated v2 (ECI).

---

## التواصل

- **المؤلفة**: شذى ياسر الجوبحي · اليمن
- **الهاتف**: +967 775 863 594

---

## الرخصة

- الكود والتصميم: MIT
- نص الرواية: جميع الحقوق محفوظة للمؤلفة © 2026
