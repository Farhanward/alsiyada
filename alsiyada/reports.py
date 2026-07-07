from __future__ import annotations


def markdown(summary: dict, title: str = "تقرير السيادة") -> str:
    m = summary.get("metrics", {})
    return "\n".join([f"# {title}", "", f"- المعالجة: `{summary.get('processed', 0)}`", f"- F1: `{m.get('f1', 0):.2%}`", f"- أخطاء: `{summary.get('errors', 0)}`", f"- p99: `{summary.get('latency_ms', {}).get('p99', 0):.4f}ms`", f"- peak memory: `{summary.get('memory_mb', {}).get('peak', 0):.2f}MB`", ""])

