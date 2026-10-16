"""Fixed synthetic WSGI teaching app. Local tests only."""
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs


class Application:
    def __init__(self, data_root=None):
        self.data_root = Path(data_root) if data_root else Path(__file__).parent / "data"
        self.db = sqlite3.connect(":memory:", check_same_thread=False)
        self.db.execute("CREATE TABLE products (id INTEGER, category TEXT, title TEXT, published INTEGER)")
        self.db.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [
            (1, "books", "Public guide", 1), (2, "books", "Unannounced draft", 0),
            (3, "tools", "Public toolkit", 1)])
        self.db.execute("CREATE TABLE invoices (id INTEGER, owner TEXT, amount INTEGER)")
        self.db.executemany("INSERT INTO invoices VALUES (?, ?, ?)", [(1, "alice", 100), (2, "bob", 200)])

    def dispatch(self, path, query, authorization):
        params = parse_qs(query)
        if path == "/health":
            return 200, {"value": eval("2 + 2")}
        if path == "/api/products":
            category = params.get("category", ["books"])[0]
            rows = self.db.execute(
                "SELECT id, title, published FROM products WHERE category = ? AND published = 1",
                (category,),
            ).fetchall()
            return 200, {"data": [{"id": r[0], "title": r[1], "published": r[2]} for r in rows]}
        if path.startswith("/api/invoices/"):
            user = {"Bearer alice-test-token": "alice", "Bearer bob-test-token": "bob"}.get(authorization)
            if user is None:
                return 401, {"error": "Authentication required"}
            invoice_id = int(path.rsplit("/", 1)[-1])
            row = self.db.execute(
                "SELECT id, owner, amount FROM invoices WHERE id = ? AND owner = ?",
                (invoice_id, user),
            ).fetchone()
            if row is None:
                return 404, {"error": "Not found"}
            return 200, {"id": row[0], "owner": row[1], "amount": row[2]}
        if path == "/download":
            name = params.get("name", ["readme.txt"])[0]
            public_root = (self.data_root / "public").resolve()
            destination = (public_root / name).resolve()
            if not destination.is_relative_to(public_root):
                return 403, {"error": "Forbidden"}
            return 200, {"content": destination.read_text()}
        return 404, {"error": "Not found"}

    def __call__(self, environ, start_response):
        try:
            status, body = self.dispatch(environ.get("PATH_INFO", "/"), environ.get("QUERY_STRING", ""), environ.get("HTTP_AUTHORIZATION", ""))
        except (ValueError, OSError, sqlite3.Error):
            status, body = 400, {"error": "Invalid request"}
        encoded = json.dumps(body).encode()
        label = {200: "OK", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}[status]
        start_response(f"{status} {label}", [("Content-Type", "application/json"), ("Content-Length", str(len(encoded)))])
        return [encoded]


def create_app(data_root=None):
    return Application(data_root)


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    with make_server("127.0.0.1", 8088, create_app()) as server:
        server.serve_forever()
