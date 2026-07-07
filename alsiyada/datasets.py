from __future__ import annotations

import json
from pathlib import Path


def convert_nvd(input_path: str | Path, out_path: str | Path, *, limit: int = 0) -> dict:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = blocked = 0
    with Path(input_path).open("r", encoding="utf-8") as handle, out.open("w", encoding="utf-8") as output:
        for index, line in enumerate(handle, start=1):
            if limit and rows >= limit:
                break
            if not line.strip():
                continue
            rec = json.loads(line)
            severity = str(rec.get("severity") or rec.get("baseSeverity") or "LOW").upper()
            high = severity in {"CRITICAL", "HIGH"}
            manifest = {
                "name": f"ai-workload-{index}",
                "data_classification": "restricted" if high else "internal",
                "cloud_models_allowed": high and index % 2 == 0,
                "audit_log": not (high and index % 5 == 0),
                "region": "EU-WEST" if high and index % 7 == 0 else "SA-RIYADH",
                "handles_pii": high,
                "tool_allowlist": not (index % 11 == 0),
                "expected_block": high and index % 2 == 0,
            }
            output.write(json.dumps(manifest, ensure_ascii=False) + "\n")
            blocked += 1 if manifest["expected_block"] else 0
            rows += 1
    return {"out": str(out.resolve()), "rows": rows, "expected_block": blocked}

