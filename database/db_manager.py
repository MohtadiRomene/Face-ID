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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs_reconnaissance (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER,
            nom             TEXT NOT NULL,
            statut          TEXT NOT NULL,
            confiance       REAL,
            date_heure      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            image_path      TEXT,
            watermark_data  TEXT
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


# ── Fonctions pour les logs de reconnaissance ──────────────────────────
def sauvegarder_log_reconnaissance(user_id, nom, statut, confiance=None, image_path=None, watermark_data=None):
    """
    Sauvegarde un log de reconnaissance faciale dans la base de données.
    """
    conn = _connect()
    conn.execute(
        """INSERT INTO logs_reconnaissance 
           (user_id, nom, statut, confiance, image_path, watermark_data) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, nom, statut, confiance, image_path, watermark_data)
    )
    conn.commit()
    conn.close()


def get_tous_logs():
    """
    Récupère tous les logs de reconnaissance triés par date décroissante.
    """
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM logs_reconnaissance ORDER BY date_heure DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_logs_par_statut(statut: str):
    """
    Récupère tous les logs avec un statut spécifique.
    """
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM logs_reconnaissance WHERE statut=? ORDER BY date_heure DESC",
        (statut,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_statistiques_logs():
    """
    Retourne les statistiques globales des logs.
    """
    conn = _connect()
    stats = {}
    total = conn.execute("SELECT COUNT(*) as cnt FROM logs_reconnaissance").fetchone()
    stats["total"] = total["cnt"] if total else 0
    
    for st in ["autorise", "refuse", "imposteur"]:
        row = conn.execute(
            "SELECT COUNT(*) as cnt FROM logs_reconnaissance WHERE statut=?",
            (st,)
        ).fetchone()
        stats[st] = row["cnt"] if row else 0
    
    conn.close()
    return stats


def supprimer_log(log_id):
    """
    Supprime un log de reconnaissance.
    """
    conn = _connect()
    conn.execute("DELETE FROM logs_reconnaissance WHERE id=?", (log_id,))
    conn.commit()
    conn.close()

