#!/usr/bin/env python3
"""Reproduce the fixture's SQL boundary failure using in-memory SQLite."""
from pathlib import Path
from contextlib import closing
import runpy
import sqlite3


def demonstrate() -> dict:
    root = Path(__file__).resolve().parent
    results = {}
    for version in ("vulnerable", "fixed"):
        implementation = runpy.run_path(str(root / version / "app.py"))["invoices_for"]
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.execute("CREATE TABLE invoices (id INTEGER, owner TEXT, amount INTEGER)")
            connection.executemany("INSERT INTO invoices VALUES (?, ?, ?)", [(1, "alice", 100), (2, "bob", 200)])
            attack = implementation(connection, "' OR 1=1 --")
            legitimate = implementation(connection, "alice")
            results[version] = {"attack_rows": len(attack), "legitimate_rows": len(legitimate)}
            assert len(legitimate) == 1 and legitimate[0][1] == "alice"
            assert len(attack) == (2 if version == "vulnerable" else 0)
    return results


if __name__ == "__main__":
    for name, result in demonstrate().items():
        print(f"{name}: attack returned {result['attack_rows']} rows; legitimate request returned {result['legitimate_rows']} row")
    print("PASS: original injection blocked; legitimate behavior preserved. Synthetic fixture only.")
