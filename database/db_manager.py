"""
Stub database/db_manager.py — remplacez par votre implémentation SQLite réelle.
Les fonctions ci-dessous sont les contrats attendus par l'interface PyQt5.
"""
import sqlite3
import os

DB_PATH = "biometrie.db"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nom        TEXT NOT NULL,
            prenom     TEXT NOT NULL,
            role       TEXT DEFAULT 'employe',
            autorise   INTEGER DEFAULT 1,
            photo_path TEXT
        )
    """)
    conn.commit()
    conn.close()


def ajouter_utilisateur(nom, prenom, photo_path=None, role="employe", autorise=1):
    conn = _connect()
    cur = conn.execute(
        "INSERT INTO utilisateurs (nom, prenom, photo_path, role, autorise) VALUES (?,?,?,?,?)",
        (nom, prenom, photo_path, role, autorise))
    conn.commit()
    uid = cur.lastrowid
    conn.close()
    return uid


def get_tous_utilisateurs():
    conn = _connect()
    rows = conn.execute("SELECT * FROM utilisateurs ORDER BY nom").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_utilisateur_par_id(uid):
    conn = _connect()
    row = conn.execute("SELECT * FROM utilisateurs WHERE id=?", (uid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def supprimer_utilisateur(uid):
    conn = _connect()
    conn.execute("DELETE FROM utilisateurs WHERE id=?", (uid,))
    conn.commit()
    conn.close()


def modifier_autorisation(uid, autorise: int):
    conn = _connect()
    conn.execute("UPDATE utilisateurs SET autorise=? WHERE id=?", (autorise, uid))
    conn.commit()
    conn.close()
