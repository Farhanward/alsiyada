from __future__ import annotations

import argparse
import json
from pathlib import Path

from .batch import evaluate
from .datasets import convert_nvd
from .policy import evaluate_manifest
from .reports import markdown


def _write_json(path: str | Path, data: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="alsiyada", description="السيادة: مدقق توافق AI محلي.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check")
    check.add_argument("--manifest-json", required=True)
    convert = sub.add_parser("convert-nvd")
    convert.add_argument("--input", default="C:/Projects/kashif/data/external/nvd_cves_12000.jsonl")
    convert.add_argument("--out", default="data/benchmarks/alsiyada_nvd_manifests.jsonl")
    convert.add_argument("--limit", type=int, default=12000)
    batch = sub.add_parser("batch")
    batch.add_argument("--input", default="data/benchmarks/alsiyada_nvd_manifests.jsonl")
    batch.add_argument("--json-out", default="reports/alsiyada_benchmark.json")
    batch.add_argument("--report", default="reports/alsiyada_benchmark.md")
    stress = sub.add_parser("stress")
    stress.add_argument("--input", default="data/benchmarks/alsiyada_nvd_manifests.jsonl")
    stress.add_argument("--repeat", type=int, default=3)
    stress.add_argument("--json-out", default="reports/alsiyada_stress.json")
    stress.add_argument("--report", default="reports/alsiyada_stress.md")
    serve = sub.add_parser("serve")
    serve.add_argument("--host")
    serve.add_argument("--port", type=int)
    sub.add_parser("version")
    args = parser.parse_args(argv)
    if args.cmd == "serve":
        from .service import run_server

        run_server(host=args.host, port=args.port)
        return 0
    if args.cmd == "version":
        from .version import __version__

        print(json.dumps({"service": "alsiyada", "version": __version__}, ensure_ascii=False))
        return 0
    if args.cmd == "check":
        print(json.dumps(evaluate_manifest(json.loads(args.manifest_json)), ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "convert-nvd":
        print(json.dumps(convert_nvd(args.input, args.out, limit=args.limit), ensure_ascii=False, indent=2))
        return 0
    if args.cmd in {"batch", "stress"}:
        summary = evaluate(args.input, repeat=getattr(args, "repeat", 1))
        _write_json(args.json_out, summary)
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(markdown(summary, "تقرير ضغط السيادة" if args.cmd == "stress" else "تقرير السيادة"), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if summary["collapse_check"]["passed"] else 2
    raise ValueError(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())

