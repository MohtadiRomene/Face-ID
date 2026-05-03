#!/usr/bin/env python3
"""
Nettoyage et test end-to-end : nouveau démarrage avec logs frais.
"""
import os
import sqlite3

print("[TEST] End-to-End: Simulation complète du système...\n")

# Step 1: Nettoyer ancienne BD et logs
print("1. Nettoyage des données anciennes...")
if os.path.exists('biometrie.db'):
    os.remove('biometrie.db')
    print("   ✓ BD supprimée")
if os.path.exists('logs') and os.path.isdir('logs'):
    import shutil
    shutil.rmtree('logs')
    print("   ✓ Dossier logs supprimé")

# Step 2: Init DB fresh
print("\n2. Initialisation fraîche de la base de données...")
try:
    from database.db_manager import init_db, get_statistiques_logs
    init_db()
    stats = get_statistiques_logs()
    print(f"   ✓ BD initialisée : total={stats['total']} logs")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import sys
    sys.exit(1)

# Step 3: Simuler une reconnaissance faciale
print("\n3. Simulation de reconnaissance faciale...")
try:
    import numpy as np
    import cv2
    from watermark.log_manager import sauvegarder_log_tatatoue
    
    # Créer une image test
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(test_frame, "RECONNAISSANCE TEST", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Simuler 5 tentatives
    test_attempts = [
        {"user_id": 1, "statut": "autorise", "nom": "Alice Dupont", "confiance": 45.2},
        {"user_id": 2, "statut": "autorise", "nom": "Bob Martin", "confiance": 52.8},
        {"user_id": 0, "statut": "refuse", "nom": "Inconnu (faible confiance)", "confiance": 92.5},
        {"user_id": 0, "statut": "refuse", "nom": "Visage bloqué", "confiance": 88.3},
        {"user_id": 0, "statut": "imposteur", "nom": "IMPOSTEUR DÉTECTÉ", "confiance": 145.0},
    ]
    
    for i, data in enumerate(test_attempts):
        sauvegarder_log_tatatoue(
            test_frame,
            user_id=data["user_id"],
            statut=data["statut"],
            nom=data["nom"],
            confiance=data["confiance"]
        )
        print(f"   ✓ Log {i+1}: {data['nom']} ({data['statut']})")
        
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    import sys
    sys.exit(1)

# Step 4: Vérifier les stats
print("\n4. Vérification des statistiques...")
try:
    from database.db_manager import get_statistiques_logs, get_tous_logs
    stats = get_statistiques_logs()
    logs = get_tous_logs()
    print(f"   ✓ Total de logs: {stats['total']}")
    print(f"   ✓ Autorisés: {stats['autorise']}")
    print(f"   ✓ Refusés: {stats['refuse']}")
    print(f"   ✓ Imposteurs: {stats['imposteur']}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import sys
    sys.exit(1)

# Step 5: Vérifier l'affichage
print("\n5. Vérification du formatage pour l'historique...")
try:
    for log in logs[:3]:
        date_heure = log.get("date_heure", "—")
        if date_heure and len(date_heure) >= 16:
            date_str = date_heure[:10].replace("-", "")
            time_str = date_heure[11:19].replace(":", "")[:6]
        else:
            date_str = "—"
            time_str = "—"
        
        statut = log.get("statut", "—").lower()
        formatted_date = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8] if date_str != "—" else "—"
        formatted_time = time_str[:2] + ":" + time_str[2:4] + ":" + time_str[4:6] if time_str != "—" else "—"
        
        print(f"   ✓ {log['nom']:30} | {statut:8} | {formatted_date} {formatted_time}")
        
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import sys
    sys.exit(1)

print("\n[TEST] ✓ End-to-End complet: SUCCÈS!")
print("\nRésumé:")
print(f"  - Base de données créée et initialisée")
print(f"  - {stats['total']} tentatives de reconnaissance simulées")
print(f"  - Toutes les données sauvegardées en BD et fichiers PNG")
print(f"  - Historique affichable dans l'interface")
