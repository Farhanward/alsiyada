"""Alsiyada compliance auditor as a local HTTP service.

``POST /api/check`` accepts ``{"manifest": {...}}`` (or the manifest fields
directly) and returns PASS/REVIEW/BLOCK with Arabic findings and actions.
"""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from typing import Any

from .http_base import BaseServiceHandler, build_server
from .policy import evaluate_manifest


def _check_route(data: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    manifest = data.get("manifest") if isinstance(data.get("manifest"), dict) else data
    if not manifest:
        return 400, {"ok": False, "error": "missing manifest payload"}
    return 200, {"ok": True, **evaluate_manifest(manifest)}


class Handler(BaseServiceHandler):
    post_routes = {"/api/check": staticmethod(_check_route)}


def create_server(host: str | None = None, port: int | None = None) -> ThreadingHTTPServer:
    return build_server(Handler, host=host, port=port)


def run_server(host: str | None = None, port: int | None = None) -> None:
    from .version import __version__

    server = create_server(host=host, port=port)
    print(f"alsiyada service v{__version__}: http://{server.server_address[0]}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
