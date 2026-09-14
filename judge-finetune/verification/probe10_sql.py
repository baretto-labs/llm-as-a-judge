#!/usr/bin/env python3
"""Probes for batch_10 SQL: ordre des colonnes d'un index composite, LIKE et préfixe."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE evenements (
    id INTEGER PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    cree_le TEXT NOT NULL,
    type TEXT NOT NULL,
    charge TEXT
);
""")
db.executemany(
    "INSERT INTO evenements (tenant_id, cree_le, type, charge) VALUES (?, ?, ?, ?)",
    [(i % 50, f"2026-0{(i % 9) + 1}-{(i % 28) + 1:02d}", f"type{i % 7}", "x" * 20) for i in range(20000)],
)
db.execute("CREATE INDEX idx_tenant_date ON evenements(tenant_id, cree_le)")
db.execute("ANALYZE")


def plan(sql, params=()):
    return db.execute("EXPLAIN QUERY PLAN " + sql, params).fetchall()[0][-1]


print("── index composite (tenant_id, cree_le)")
print("   filtre sur les deux colonnes :")
print("     ", plan("SELECT * FROM evenements WHERE tenant_id = 3 AND cree_le >= '2026-05-01'"))
print("   filtre sur la première colonne seule :")
print("     ", plan("SELECT * FROM evenements WHERE tenant_id = 3"))
print("   filtre sur la seconde colonne seule :")
print("     ", plan("SELECT * FROM evenements WHERE cree_le >= '2026-05-01'"))
print("   tri sur la seconde après égalité sur la première :")
print("     ", plan("SELECT * FROM evenements WHERE tenant_id = 3 ORDER BY cree_le"))
print("   tri sur la seconde sans filtre sur la première :")
print("     ", plan("SELECT * FROM evenements ORDER BY cree_le"))

print("── LIKE et utilisation d'index")
db.execute("CREATE INDEX idx_type ON evenements(type)")
db.execute("ANALYZE")
print("   LIKE 'type1%'  :", plan("SELECT * FROM evenements WHERE type LIKE 'type1%'"))
print("   LIKE '%type1'  :", plan("SELECT * FROM evenements WHERE type LIKE '%type1'"))
print("   égalité stricte :", plan("SELECT * FROM evenements WHERE type = 'type1'"))

print("── COUNT et index couvrant")
print("   COUNT(*) filtré sur tenant :", plan("SELECT COUNT(*) FROM evenements WHERE tenant_id = 3"))
print("   SELECT charge filtré       :", plan("SELECT charge FROM evenements WHERE tenant_id = 3"))
