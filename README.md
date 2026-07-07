# السيادة AlSiyada

السيادة مدقق توافق محلي لمنصات ووكلاء AI على أرض العميل: يقرأ manifest ويصدر `PASS/REVIEW/BLOCK` مع أسباب عربية وإجراءات.

## آلية العمل

1. `check` يفحص manifest JSON.
2. `convert-nvd` يحول NVD إلى manifests اختبارية.
3. `batch/stress` يقيسان دقة قرارات الحظر والانهيار.

## تشغيل سريع

```powershell
python -m alsiyada.cli check --manifest-json "{\"data_classification\":\"restricted\",\"cloud_models_allowed\":true}"
python -m alsiyada.cli convert-nvd
python -m alsiyada.cli batch
```

## بيانات الاختبار

المصدر: NVD CVE API 2.0 المحفوظ في `C:\Projects\kashif` بعدد 12,000 سجل.

## آخر نتائج

- الاختبارات الذاتية: 3/3 ناجحة.
- بيانات الإنترنت: 12,000 CVE حُولت إلى manifests امتثال، منها 2,650 حظر متوقع.
- Benchmark: 12,000 معالجة، Precision/Recall/F1=100%، errors=0، p99=0.0169ms.
- Stress: 36,000 معالجة، errors=0، p99=0.0142ms، peak memory=1.18MB.

## تحسينات إنتاجية 2026-07-04

- القرار يفصل بين `BLOCK` للمخالفات الحرجة و`REVIEW` للمخاطر العالية غير القاطعة.
- السياسات تغطي: حساسية البيانات، السحابة، PII/region، audit log، tool allowlist.
- batch/stress يقيسان precision/recall/F1 لقرارات الحظر.

## التشغيل المؤسسي (Enterprise) — v1.0.0

- **خدمة امتثال HTTP**: `python -m alsiyada.cli serve` → `POST /api/check {"manifest": {...}}` يعيد `PASS/REVIEW/BLOCK` مع إجراءات عربية.
- **نقاط فحص**: `/api/health` (مفتوح) · `/api/version` · `/api/metrics`.
- **تهيئة عبر البيئة**: متغيرات `ALSIYADA_*` — انظر `docs/OPERATIONS.md`.
- **مصادقة**: `ALSIYADA_API_KEY` → ترويسة `X-API-Key`. **سجلات JSON**: `logs\alsiyada.service.jsonl`.
