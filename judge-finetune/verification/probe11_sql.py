#!/usr/bin/env python3
"""Probes for batch_11 SQL: sémantique de NULL, NOT IN, agrégats et tri."""
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE clients (id INTEGER PRIMARY KEY, nom TEXT, parrain_id INTEGER);
INSERT INTO clients VALUES (1, 'Ana', NULL), (2, 'Bob', 1), (3, 'Cid', 2), (4, 'Dan', NULL);
CREATE TABLE commandes (id INTEGER PRIMARY KEY, client_id INTEGER, montant REAL);
INSERT INTO commandes VALUES (1, 1, 10.0), (2, 2, NULL), (3, 2, 30.0);
""")
q = lambda sql: db.execute(sql).fetchall()

print("── NOT IN avec une sous-requête contenant NULL")
print("   clients qui ne parrainent personne, via NOT IN :")
print("     ", q("SELECT id, nom FROM clients WHERE id NOT IN (SELECT parrain_id FROM clients)"))
print("   la sous-requête contient :", [r[0] for r in q("SELECT parrain_id FROM clients")])
print("   même intention avec NOT EXISTS :")
print("     ", q("""SELECT c.id, c.nom FROM clients c
                    WHERE NOT EXISTS (SELECT 1 FROM clients p WHERE p.parrain_id = c.id)"""))
print("   avec NOT IN et filtrage des NULL :")
print("     ", q("SELECT id, nom FROM clients WHERE id NOT IN (SELECT parrain_id FROM clients WHERE parrain_id IS NOT NULL)"))

print("── comparaisons impliquant NULL")
for expr in ["NULL = NULL", "NULL <> NULL", "NULL IS NULL", "1 IN (1, NULL)", "2 IN (1, NULL)",
             "2 NOT IN (1, NULL)", "NULL || 'x'", "COALESCE(NULL, 'défaut')"]:
    valeur = q(f"SELECT {expr}")[0][0]
    print(f"   {expr:<26} -> {valeur!r}")

print("── agrégats et NULL")
print("   SUM, AVG, COUNT sur une colonne avec un NULL :")
print("     ", q("SELECT SUM(montant), AVG(montant), COUNT(montant), COUNT(*) FROM commandes WHERE client_id = 2"))
print("   SUM sur un ensemble vide :", q("SELECT SUM(montant) FROM commandes WHERE client_id = 99"))
print("   COUNT sur un ensemble vide :", q("SELECT COUNT(*) FROM commandes WHERE client_id = 99"))
print("   moyenne calculée à la main (SUM/COUNT(*)) :",
      q("SELECT SUM(montant) / COUNT(*) FROM commandes WHERE client_id = 2"))

print("── tri et NULL")
print("   ORDER BY montant ASC  :", q("SELECT id, montant FROM commandes ORDER BY montant"))
print("   ORDER BY montant DESC :", q("SELECT id, montant FROM commandes ORDER BY montant DESC"))
print("   ORDER BY montant DESC NULLS LAST :",
      q("SELECT id, montant FROM commandes ORDER BY montant DESC NULLS LAST"))

print("── contrainte d'unicité et NULL")
db.executescript("CREATE TABLE codes (code TEXT UNIQUE); INSERT INTO codes VALUES (NULL), (NULL), ('a');")
print("   deux NULL acceptés dans une colonne UNIQUE :", q("SELECT COUNT(*) FROM codes"))
try:
    db.execute("INSERT INTO codes VALUES ('a')")
except sqlite3.IntegrityError as e:
    print(f"   doublon non nul refusé : IntegrityError — {e}")
