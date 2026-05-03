#!/usr/bin/env python3
"""
Vérifier la structure et le contenu de la base de données.
"""
import sqlite3

conn = sqlite3.connect('biometrie.db')
cur = conn.cursor()

print("Tables dans biometrie.db:")
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for t in tables:
    print(f"  - {t[0]}")

print("\nColonnes dans logs_reconnaissance:")
cur.execute("PRAGMA table_info(logs_reconnaissance)")
columns = cur.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

print("\nLogs dans logs_reconnaissance:")
cur.execute("SELECT COUNT(*) FROM logs_reconnaissance")
count = cur.fetchone()[0]
print(f"  Total: {count}")

print("\nContenu des logs:")
cur.execute("SELECT id, nom, statut, date_heure FROM logs_reconnaissance ORDER BY date_heure DESC")
for row in cur.fetchall():
    print(f"  ID={row[0]} | {row[1]} | {row[2]} | {row[3]}")

conn.close()
print("\n✓ Vérification terminée")
