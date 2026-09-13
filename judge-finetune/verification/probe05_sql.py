#!/usr/bin/env python3
"""Probes for batch_05 SQL: N+1, pagination OFFSET vs keyset, index manquant."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT);
""")
db.executemany("INSERT INTO authors VALUES (?, ?)", [(i, f"Auteur {i:03d}") for i in range(1, 101)])
db.executemany("INSERT INTO books VALUES (?, ?, ?)",
               [(i, (i % 100) + 1, f"Livre {i}") for i in range(1, 1001)])

queries = []
db.set_trace_callback(lambda s: queries.append(s))

print("── N+1")
queries.clear()
authors = db.execute("SELECT id, name FROM authors").fetchall()
for author_id, _ in authors:
    db.execute("SELECT title FROM books WHERE author_id = ?", (author_id,)).fetchall()
print(f"   boucle par auteur : {len(queries)} requêtes pour {len(authors)} auteurs")

queries.clear()
db.execute("""SELECT a.id, a.name, b.title FROM authors a
              LEFT JOIN books b ON b.author_id = a.id ORDER BY a.id""").fetchall()
print(f"   jointure unique   : {len(queries)} requête")
db.set_trace_callback(None)

print("── pagination OFFSET pendant une insertion")
page1 = db.execute("SELECT id FROM books ORDER BY id LIMIT 3 OFFSET 0").fetchall()
db.execute("INSERT INTO books VALUES (0, 1, 'Livre inséré en tête')")
page2_offset = db.execute("SELECT id FROM books ORDER BY id LIMIT 3 OFFSET 3").fetchall()
last_id = page1[-1][0]
page2_keyset = db.execute(
    "SELECT id FROM books WHERE id > ? ORDER BY id LIMIT 3", (last_id,)).fetchall()
print(f"   page 1                    : {[r[0] for r in page1]}")
print(f"   page 2 par OFFSET         : {[r[0] for r in page2_offset]}")
print(f"   page 2 par curseur (id >) : {[r[0] for r in page2_keyset]}")
print(f"   doublon avec OFFSET ? {bool(set(r[0] for r in page1) & set(r[0] for r in page2_offset))}")

print("── index manquant")
db.execute("ANALYZE")
plan_before = db.execute(
    "EXPLAIN QUERY PLAN SELECT * FROM books WHERE author_id = 42").fetchall()
print(f"   sans index sur author_id : {plan_before[0][-1]}")
db.execute("CREATE INDEX idx_books_author ON books(author_id)")
db.execute("ANALYZE")
plan_after = db.execute(
    "EXPLAIN QUERY PLAN SELECT * FROM books WHERE author_id = 42").fetchall()
print(f"   avec index               : {plan_after[0][-1]}")
