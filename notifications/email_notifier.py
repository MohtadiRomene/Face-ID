import datetime
import os
import smtplib
from email.message import EmailMessage
from typing import Optional


_LAST_SENT_AT: dict[str, datetime.datetime] = {}


def _load_env_file() -> None:
    """
    Charge un fichier .env simple (KEY=VALUE) si présent.
    Ne remplace pas les variables d'environnement déjà définies.
    """
    env_path = ".env"
    if not os.path.exists(env_path):
        return

    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as e:
        print(f"[EMAIL] Impossible de lire .env: {e}")


def _as_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _should_notify(statut: str) -> bool:
    if statut == "imposteur":
        return True
    notify_refuse = _as_bool(os.getenv("SMTP_NOTIFY_REFUSE"), default=True)
    return statut == "refuse" and notify_refuse


def _is_rate_limited(statut: str) -> bool:
    cooldown_raw = os.getenv("SMTP_NOTIFY_COOLDOWN_SECONDS", "30")
    try:
        cooldown_seconds = max(0, int(cooldown_raw))
    except ValueError:
        cooldown_seconds = 30

    if cooldown_seconds == 0:
        return False

    now = datetime.datetime.now()
    last = _LAST_SENT_AT.get(statut)
    if not last:
        _LAST_SENT_AT[statut] = now
        return False

    delta = (now - last).total_seconds()
    if delta < cooldown_seconds:
        return True

    _LAST_SENT_AT[statut] = now
    return False


def envoyer_notification_acces(
    statut: str,
    nom: str,
    user_id: int,
    confiance: Optional[float],
    image_path: str,
) -> bool:
    """
    Envoie un email SMTP pour les événements sensibles.
    Retourne True si envoi effectué, False sinon.
    """
    _load_env_file()

    if not _as_bool(os.getenv("SMTP_ENABLED"), default=False):
        return False

    if not _should_notify(statut):
        return False

    if _is_rate_limited(statut):
        print(
            f"[EMAIL] Notification ignorée (cooldown actif) pour statut={statut}"
        )
        return False

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", username or "")
    recipient = os.getenv("SMTP_TO")
    use_tls = _as_bool(os.getenv("SMTP_USE_TLS"), default=True)

    if not host or not sender or not recipient:
        print(
            "[EMAIL] Config SMTP incomplète. "
            "Variables requises: SMTP_HOST, SMTP_FROM, SMTP_TO"
        )
        return False

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    confidence_text = (
        f"{confiance:.2f}" if isinstance(confiance, (int, float)) else "N/A"
    )
    severity = "CRITIQUE" if statut == "imposteur" else "AVERTISSEMENT"

    subject = f"[BiometriX][{severity}] Événement {statut.upper()}"
    body = (
        "Une alerte de contrôle d'accès a été générée.\n\n"
        f"Date/Heure : {timestamp}\n"
        f"Statut     : {statut}\n"
        f"Nom        : {nom}\n"
        f"User ID    : {user_id}\n"
        f"Confiance  : {confidence_text}\n"
        f"Image log  : {image_path}\n"
    )

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)
        print(f"[EMAIL] Notification envoyée ({statut}) vers {recipient}")
        return True
    except Exception as e:
        print(f"[EMAIL] Échec envoi SMTP: {e}")
        return False
