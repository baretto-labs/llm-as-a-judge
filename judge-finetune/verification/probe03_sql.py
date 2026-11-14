#!/usr/bin/env python3
"""Probe for batch_03 b03-009: a function applied to an indexed column blocks index usage."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE orders (id INTEGER PRIMARY KEY, created_at TEXT NOT NULL, total REAL);
CREATE INDEX idx_orders_created_at ON orders(created_at);
""")
rows = [(i, f"2026-01-{(i % 28) + 1:02d} 1{i % 10}:00:00", i * 1.5) for i in range(1, 5001)]
db.executemany("INSERT INTO orders VALUES (?, ?, ?)", rows)
db.execute("ANALYZE")

queries = {
    "DATE(created_at) = '2026-01-05'":
        "SELECT COUNT(*) FROM orders WHERE DATE(created_at) = '2026-01-05'",
    "created_at >= '2026-01-05' AND < '2026-01-06'":
        "SELECT COUNT(*) FROM orders WHERE created_at >= '2026-01-05' AND created_at < '2026-01-06'",
    "strftime('%Y-%m', created_at) = '2026-01'":
        "SELECT COUNT(*) FROM orders WHERE strftime('%Y-%m', created_at) = '2026-01'",
}
for label, sql in queries.items():
    plan = db.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    count = db.execute(sql).fetchone()[0]
    print(f"{label}\n   plan  : {plan[0][-1]}\n   count : {count}")
