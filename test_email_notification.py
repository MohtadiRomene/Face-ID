#!/usr/bin/env python3
"""
Test unitaire simple des notifications email SMTP.
"""
from notifications.email_notifier import envoyer_notification_acces


def main() -> None:
    sent = envoyer_notification_acces(
        statut="imposteur",
        nom="Test Imposteur",
        user_id=0,
        confiance=150.0,
        image_path="logs/test_imposteur.png",
    )
    if sent:
        print("[TEST EMAIL] Notification envoyée avec succès.")
    else:
        print(
            "[TEST EMAIL] Notification non envoyée "
            "(SMTP désactivé/config absent/cooldown)."
        )


if __name__ == "__main__":
    main()
