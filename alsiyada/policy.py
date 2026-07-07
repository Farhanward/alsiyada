from __future__ import annotations


def evaluate_manifest(manifest: dict) -> dict:
    findings = []
    data = str(manifest.get("data_classification") or "public").lower()
    cloud = bool(manifest.get("cloud_models_allowed", False))
    audit = bool(manifest.get("audit_log", False))
    region = str(manifest.get("region") or "").upper()
    pii = bool(manifest.get("handles_pii", False))
    tool_allowlist = bool(manifest.get("tool_allowlist", False))
    if data in {"secret", "restricted"} and cloud:
        findings.append(("critical", "بيانات حساسة مع نماذج سحابية", "استخدم نموذجاً محلياً أو تعقيماً وبوابة وسيطة."))
    if pii and not region.startswith("SA"):
        findings.append(("high", "PII خارج نطاق مقبول", "حدد منطقة استضافة محلية/مصرح بها."))
    if not audit:
        findings.append(("high", "غياب سجل تدقيق", "فعّل سجل hash-chain أو سجل مركزي قابل للمراجعة."))
    if not tool_allowlist:
        findings.append(("medium", "أدوات بلا قائمة سماح", "فعّل AEGIS أو سياسة allowlist."))
    if any(level == "critical" for level, _, _ in findings):
        decision = "BLOCK"
    elif any(level == "high" for level, _, _ in findings):
        decision = "REVIEW"
    else:
        decision = "PASS"
    return {"decision": decision, "findings": [{"severity": a, "title": b, "action": c} for a, b, c in findings], "score": max(0, 100 - 35 * len(findings))}

