import sqlite3
import os
from datetime import datetime

DB_PATH = "biometrie.db"

def get_connection():
    """Retourne une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # accès par nom de colonne
    return conn

def init_db():
    """Crée toutes les tables si elles n'existent pas."""
    conn = get_connection()
    cursor = conn.cursor()

    # Table des utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nom             TEXT NOT NULL,
            prenom          TEXT NOT NULL,
            photo_path      TEXT,
            role            TEXT DEFAULT 'user',
            autorise        INTEGER DEFAULT 1,
            date_inscription TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table des logs d'accès
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs_acces (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER,
            date_heure      TEXT DEFAULT CURRENT_TIMESTAMP,
            statut          TEXT NOT NULL,
            image_log_path  TEXT,
            watermark_data  TEXT,
            verifie         INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES utilisateurs(id)
        )
    """)

    # Table des alertes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id      INTEGER,
            type_alerte TEXT NOT NULL,
            date_heure  TEXT DEFAULT CURRENT_TIMESTAMP,
            email_envoye TEXT DEFAULT 'non',
            FOREIGN KEY (log_id) REFERENCES logs_acces(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Base de données initialisée avec succès.")

# ─── Fonctions UTILISATEURS ─────────────────────────────────────

def ajouter_utilisateur(nom, prenom, photo_path=None, role="user", autorise=1):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO utilisateurs (nom, prenom, photo_path, role, autorise)
        VALUES (?, ?, ?, ?, ?)
    """, (nom, prenom, photo_path, role, autorise))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    print(f"[DB] Utilisateur ajouté : {prenom} {nom} (ID={user_id})")
    return user_id

def get_tous_utilisateurs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs ORDER BY nom")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_utilisateur_par_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilisateurs WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def modifier_autorisation(user_id, autorise):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE utilisateurs SET autorise = ? WHERE id = ?",
                   (autorise, user_id))
    conn.commit()
    conn.close()

def supprimer_utilisateur(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM utilisateurs WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    print(f"[DB] Utilisateur supprimé (ID={user_id})")

# ─── Fonctions LOGS ─────────────────────────────────────────────

def ajouter_log(user_id, statut, image_log_path=None, watermark_data=None):
    """
    statut : 'autorise' | 'refuse' | 'imposteur'
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs_acces (user_id, statut, image_log_path, watermark_data)
        VALUES (?, ?, ?, ?)
    """, (user_id, statut, image_log_path, watermark_data))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_logs_recents(limite=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT l.*, u.nom, u.prenom
        FROM logs_acces l
        LEFT JOIN utilisateurs u ON l.user_id = u.id
        ORDER BY l.date_heure DESC
        LIMIT ?
    """, (limite,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def marquer_log_verifie(log_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE logs_acces SET verifie = 1 WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()

# ─── Fonctions ALERTES ──────────────────────────────────────────

def ajouter_alerte(log_id, type_alerte):
    """
    type_alerte : 'acces_refuse' | 'imposteur' | 'tentative_multiple'
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alertes (log_id, type_alerte)
        VALUES (?, ?)
    """, (log_id, type_alerte))
    conn.commit()
    alerte_id = cursor.lastrowid
    conn.close()
    return alerte_id

def get_alertes_non_envoyees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, l.statut, l.image_log_path
        FROM alertes a
        JOIN logs_acces l ON a.log_id = l.id
        WHERE a.email_envoye = 'non'
        ORDER BY a.date_heure DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def marquer_alerte_envoyee(alerte_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE alertes SET email_envoye = 'oui' WHERE id = ?",
                   (alerte_id,))
    conn.commit()
    conn.close()