#!/usr/bin/env python3
"""Fact-checks every executable claim made in batch_02 (Python + SQL examples)."""
import re
import sqlite3

ok = lambda label, cond, detail="": print(f"{'OK ' if cond else 'KO '} {label} {detail}")

# ── b02-001 / b02-002 : injection SQL ────────────────────────────────────────
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, name TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?, ?)",
                 [(1, "alice@example.com", "Alice"), (2, "o'brien@example.com", "O'Brien")])


def vulnerable(conn, email):
    return conn.execute(f"SELECT id, email, name FROM users WHERE email = '{email}'").fetchone()


def safe(conn, email):
    return conn.execute("SELECT id, email, name FROM users WHERE email = ?", (email,)).fetchone()


print("── b02-001 / b02-002")
ok("nominal vulnérable", vulnerable(conn, "alice@example.com") == (1, "alice@example.com", "Alice"))
ok("injection renvoie la 1re ligne", vulnerable(conn, "x' OR '1'='1") == (1, "alice@example.com", "Alice"),
   repr(vulnerable(conn, "x' OR '1'='1")))
try:
    vulnerable(conn, "o'brien@example.com")
    ok("apostrophe casse la requête", False, "aucune exception levée")
except sqlite3.OperationalError as e:
    ok("apostrophe casse la requête", True, f"OperationalError: {e}")
ok("paramétré : nominal", safe(conn, "alice@example.com") == (1, "alice@example.com", "Alice"))
ok("paramétré : absent -> None", safe(conn, "nobody@example.com") is None)
ok("paramétré : injection neutralisée", safe(conn, "x' OR '1'='1") is None)
ok("paramétré : apostrophe OK", safe(conn, "o'brien@example.com") == (2, "o'brien@example.com", "O'Brien"))

# ── b02-005 : `tags or []` casse sur une liste vide fournie ──────────────────
print("── b02-005")


def add_tag_buggy(tag, tags=None):
    tags = tags or []
    tags.append(tag)
    return tags


def add_tag_correct(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


mine = []
returned = add_tag_buggy("a", mine)
ok("`or []` renvoie ['a']", returned == ["a"])
ok("`or []` ne modifie pas la liste appelante", mine == [], f"mine={mine!r}")
mine2 = []
add_tag_correct("a", mine2)
ok("`is None` modifie bien la liste appelante", mine2 == ["a"], f"mine2={mine2!r}")
ok("pas d'accumulation entre appels", add_tag_buggy("x") == ["x"] and add_tag_buggy("y") == ["y"])

# ── b02-006 / b02-007 : COUNT(*) vs COUNT(colonne) sur LEFT JOIN ─────────────
print("── b02-006 / b02-007")
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT);
INSERT INTO authors VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Carol');
INSERT INTO books VALUES (1, 1, 'A1'), (2, 1, 'A2'), (3, 2, 'B1');
""")
star = db.execute("""SELECT a.id, a.name, COUNT(*) AS book_count FROM authors a
                     LEFT JOIN books b ON b.author_id = a.id GROUP BY a.id, a.name
                     ORDER BY book_count DESC""").fetchall()
col = db.execute("""SELECT a.id, a.name, COUNT(b.id) AS book_count FROM authors a
                    LEFT JOIN books b ON b.author_id = a.id GROUP BY a.id, a.name
                    ORDER BY book_count DESC, a.name""").fetchall()
ok("COUNT(*) donne 1 pour Carol", (3, "Carol", 1) in star, str(star))
ok("COUNT(b.id) donne 0 pour Carol", (3, "Carol", 0) in col, str(col))
ok("comptes corrects avec COUNT(b.id)", col == [(1, "Alice", 2), (2, "Bob", 1), (3, "Carol", 0)])

# ── b02-008 : parse_duration ─────────────────────────────────────────────────
print("── b02-008")
_PATTERN = re.compile(r"(\d+)([hms])")
_FACTORS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(s):
    """Convertit une durée compacte ('1h30m') en secondes."""
    if not isinstance(s, str) or not s:
        raise ValueError(f"Durée invalide : {s!r}")
    matches = _PATTERN.findall(s)
    if not matches or "".join(n + u for n, u in matches) != s:
        raise ValueError(f"Durée invalide : {s!r}")
    return sum(int(n) * _FACTORS[u] for n, u in matches)


ok("1h30m -> 5400", parse_duration("1h30m") == 5400)
ok("45s -> 45", parse_duration("45s") == 45)
ok("2h -> 7200", parse_duration("2h") == 7200)
for bad in ["1h 30m", "1h!!", "abc", "", "2d", None, "1h30x"]:
    try:
        parse_duration(bad)
        ok(f"{bad!r} lève ValueError", False, "aucune exception")
    except ValueError:
        ok(f"{bad!r} lève ValueError", True)
    except TypeError as e:
        ok(f"{bad!r} lève ValueError", False, f"TypeError à la place: {e}")
