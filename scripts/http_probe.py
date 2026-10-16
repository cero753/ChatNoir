#!/usr/bin/env python3
"""Exercise only a supplied local fixture through an ephemeral loopback HTTP server."""
import argparse
import importlib.util
import json
from pathlib import Path
import threading
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, ProxyHandler, Request
from wsgiref.simple_server import make_server, WSGIRequestHandler


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass


def probe(directory):
    """Loads target code: use only with trusted, authorized synthetic fixture copies."""
    directory = Path(directory).resolve()
    spec = importlib.util.spec_from_file_location("local_fixture", directory / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.create_app(directory / "data")
    server = make_server("127.0.0.1", 0, app, handler_class=QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    opener = build_opener(ProxyHandler({}))  # Never route fixture traffic through environment proxies.

    def get(path, token=None):
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        request = Request(f"http://127.0.0.1:{server.server_port}" + path, headers=headers)
        try:
            response = opener.open(request, timeout=5)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    try:
        status, catalog = get("/api/products?" + urlencode({"category": "books"}))
        legit_catalog = status == 200 and [r["id"] for r in catalog.get("data", [])] == [1]
        status, injection = get("/api/products?" + urlencode({"category": "' OR 1=1 --"}))
        sql_blocked = status in {400, 403} or (status == 200 and not any(r.get("published") == 0 for r in injection.get("data", [])))
        status, invoice = get("/api/invoices/1", "alice-test-token")
        legit_invoice = status == 200 and invoice.get("owner") == "alice"
        status, cross_user = get("/api/invoices/2", "alice-test-token")
        idor_blocked = status in {403, 404}
        status, unauthenticated = get("/api/invoices/1")
        no_session_blocked = status == 401
        status, document = get("/download?" + urlencode({"name": "readme.txt"}))
        legit_download = status == 200 and document.get("content", "").strip() == "Public fixture document."
        status, traversal = get("/download?" + urlencode({"name": "../internal/notes.txt"}))
        traversal_blocked = status in {400, 403, 404}
        status, health = get("/health")
        legit_health = status == 200 and health.get("value") == 4
        return {"sql_injection_blocked": sql_blocked, "cross_user_invoice_blocked": idor_blocked,
                "path_traversal_blocked": traversal_blocked,
                "legitimate_catalog": legit_catalog, "legitimate_invoice": legit_invoice,
                "unauthenticated_invoice_blocked": no_session_blocked,
                "legitimate_download": legit_download, "health": legit_health}
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
        app.db.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="trusted local synthetic fixture directory; target code is executed")
    args = parser.parse_args()
    results = probe(args.fixture)
    print(json.dumps(results, indent=2))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
