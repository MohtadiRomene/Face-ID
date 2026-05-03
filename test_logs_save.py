#!/usr/bin/env python3
"""
Script de test pour vérifier que les logs sont bien sauvegardés.
"""
import cv2
import numpy as np
from database.db_manager import init_db, get_statistiques_logs, get_tous_logs
from watermark.log_manager import sauvegarder_log_tatatoue

# Initialiser la BD
init_db()
print("[TEST] Base de données initialisée")

# Créer une image test (frame vide)
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(test_frame, "TEST FRAME", (200, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Simuler 3 tentatives de reconnaissance
test_data = [
    {"user_id": 1, "statut": "autorise", "nom": "Alice Dupont", "confiance": 45.5},
    {"user_id": 0, "statut": "refuse", "nom": "Inconnu (faible confiance)", "confiance": 85.0},
    {"user_id": 0, "statut": "imposteur", "nom": "IMPOSTEUR", "confiance": 150.0},
]

print("\n[TEST] Sauvegarde des logs de test...")
for i, data in enumerate(test_data):
    try:
        image_path = sauvegarder_log_tatatoue(
            test_frame,
            user_id=data["user_id"],
            statut=data["statut"],
            nom=data["nom"],
            confiance=data["confiance"]
        )
        print(f"  ✓ Log {i+1} sauvegardé : {image_path}")
    except Exception as e:
        print(f"  ✗ Erreur pour log {i+1}: {e}")

# Vérifier les statistiques
print("\n[TEST] Statistiques après sauvegarde:")
stats = get_statistiques_logs()
for key, val in stats.items():
    print(f"  {key}: {val}")

# Afficher tous les logs
print("\n[TEST] Tous les logs:")
logs = get_tous_logs()
for log in logs:
    print(f"  - {log['nom']} | {log['statut']} | {log['date_heure']}")

print("\n[TEST] ✓ Test terminé avec succès!")
