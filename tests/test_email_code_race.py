"""Concurrency proof against real independent SQLite connections and stored rows."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import runpy
import sqlite3
import tempfile
import threading
import unittest

demo = runpy.run_path(str(Path(__file__).resolve().parents[1]
                            / "examples/email-code-race/demo.py"))


class EmailCodeRaceTests(unittest.TestCase):
    def test_vulnerable_two_and_eight_requests_create_multiple_sessions(self):
        for workers in (2, 8):
            with self.subTest(workers=workers):
                self.assertEqual(demo["run_case"](demo["consume_vulnerable"], workers), {
                    "concurrent_sessions": workers, "stored_sessions": workers,
                    "replay_sessions": 0, "legitimate_sessions": 1,
                })

    def test_fixed_two_and_eight_requests_persist_exactly_one_session(self):
        for workers in (2, 8):
            with self.subTest(workers=workers):
                self.assertEqual(demo["run_case"](demo["consume_fixed"], workers), {
                    "concurrent_sessions": 1, "stored_sessions": 1,
                    "replay_sessions": 0, "legitimate_sessions": 1,
                })

    def test_fixed_rejects_wrong_expired_and_exhausted_codes_without_sessions(self):
        for name, seed_options, supplied_code in (
            ("wrong", {}, "000000"), ("expired", {"expires_in": -1}, demo["CODE"]),
            ("exhausted", {"attempts": demo["MAX_ATTEMPTS"]}, demo["CODE"]),
        ):
            with self.subTest(case=name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path, **seed_options)
                self.assertFalse(demo["sign_in"](path, demo["consume_fixed"], code=supplied_code))
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)
                    self.assertIsNone(db.execute("SELECT consumed_at FROM codes").fetchone()[0])

    def test_fixed_rechecks_expiry_and_attempts_when_claiming_stale_read(self):
        for update in ("expires_at = 0", "attempts = 5"):
            with self.subTest(update=update), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path)

                def change_eligibility():
                    with closing(sqlite3.connect(path)) as db, db:
                        db.execute(f"UPDATE codes SET {update}")  # Fixed test literals only.

                self.assertFalse(demo["sign_in"](
                    path, demo["consume_fixed"], after_read=change_eligibility))
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)

    def test_wrong_codes_exhaust_budget_and_block_correct_code(self):
        for consume in (demo["consume_vulnerable"], demo["consume_fixed"]):
            with self.subTest(consume=consume.__name__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path)
                for attempt in range(1, demo["MAX_ATTEMPTS"] + 1):
                    self.assertFalse(demo["sign_in"](path, consume, code="000000"))
                    with closing(sqlite3.connect(path)) as db:
                        self.assertEqual(db.execute("SELECT attempts FROM codes").fetchone()[0], attempt)
                self.assertFalse(demo["sign_in"](path, consume))
                self.assertFalse(demo["sign_in"](path, consume, code="000000"))
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT attempts, consumed_at FROM codes").fetchone(),
                                     (demo["MAX_ATTEMPTS"], None))
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)

    def test_correct_code_before_limit_still_creates_session(self):
        for consume in (demo["consume_vulnerable"], demo["consume_fixed"]):
            with self.subTest(consume=consume.__name__), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path)
                for _ in range(demo["MAX_ATTEMPTS"] - 1):
                    self.assertFalse(demo["sign_in"](path, consume, code="000000"))
                self.assertTrue(demo["sign_in"](path, consume))
                self.assertFalse(demo["sign_in"](path, consume))
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT attempts FROM codes").fetchone()[0], demo["MAX_ATTEMPTS"] - 1)
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 1)

    def test_concurrent_wrong_codes_count_without_lost_updates_or_overshoot(self):
        for workers, initial, expected in ((2, 0, 2), (8, 0, 5), (2, 4, 5)):
            with self.subTest(workers=workers, initial=initial), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path, attempts=initial)
                barrier = threading.Barrier(workers, timeout=10)
                with ThreadPoolExecutor(max_workers=workers) as pool:
                    futures = [pool.submit(demo["sign_in"], path, demo["consume_fixed"],
                                           code="000000", after_read=barrier.wait) for _ in range(workers)]
                    self.assertEqual([f.result(timeout=15) for f in futures], [False] * workers)
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT attempts FROM codes").fetchone()[0], expected)
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)
                if expected == demo["MAX_ATTEMPTS"]:
                    self.assertFalse(demo["sign_in"](path, demo["consume_fixed"]))

    def test_fixed_claim_rejects_correct_snapshot_after_real_failures_exhaust_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "codes.sqlite"
            demo["seed"](path)

            def exhaust_budget():
                for _ in range(demo["MAX_ATTEMPTS"]):
                    self.assertFalse(demo["sign_in"](path, demo["consume_fixed"], code="000000"))

            self.assertFalse(demo["sign_in"](path, demo["consume_fixed"], after_read=exhaust_budget))
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT attempts, consumed_at FROM codes").fetchone(),
                                 (demo["MAX_ATTEMPTS"], None))
                self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)

    def test_failed_attempt_does_not_update_consumed_or_expired_stale_code(self):
        for update in ("expires_at = 0", "consumed_at = 1"):
            with self.subTest(update=update), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "codes.sqlite"
                demo["seed"](path)

                def change_eligibility():
                    with closing(sqlite3.connect(path)) as db, db:
                        db.execute(f"UPDATE codes SET {update}")  # Fixed test literals only.

                self.assertFalse(demo["sign_in"](
                    path, demo["consume_fixed"], code="000000", after_read=change_eligibility))
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute("SELECT attempts FROM codes").fetchone()[0], 0)
                    self.assertEqual(db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0], 0)
                    column = "expires_at" if update.startswith("expires_at") else "consumed_at"
                    self.assertEqual(db.execute(f"SELECT {column} FROM codes").fetchone()[0],
                                     0 if column == "expires_at" else 1)


if __name__ == "__main__":
    unittest.main()
