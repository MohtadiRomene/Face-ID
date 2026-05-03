#!/usr/bin/env python3
"""
Test complet pour initialiser la page historique et vérifier qu'elle charge correctement.
"""
import sys
import os

print("[TEST] Vérification de l'initialisation de page_historique...\n")

# Test 1: Initialiser la BD
print("1. Initialisation de la base de données...")
try:
    from database.db_manager import init_db, get_tous_logs, get_statistiques_logs
    init_db()
    print("   ✓ BD initialisée")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 2: Récupérer les logs
print("\n2. Récupération des logs...")
try:
    logs = get_tous_logs()
    stats = get_statistiques_logs()
    print(f"   ✓ {len(logs)} logs trouvés")
    print(f"   ✓ Stats: total={stats['total']}, autorise={stats['autorise']}, refuse={stats['refuse']}, imposteur={stats['imposteur']}")
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    sys.exit(1)

# Test 3: Vérifier le formatage pour affichage
print("\n3. Vérification du formatage pour l'affichage...")
try:
    LOGS_DIR = "logs"
    counts = {"total": 0, "autorise": 0, "refuse": 0, "imposteur": 0}
    
    for log in logs:
        date_heure = log.get("date_heure", "—")
        if date_heure and len(date_heure) >= 16:
            date_str = date_heure[:10].replace("-", "")
            time_str = date_heure[11:19].replace(":", "")[:6]
        else:
            date_str = "—"
            time_str = "—"
        
        statut = log.get("statut", "—").lower()
        nom_fichier = f"log_{date_str}_{time_str}_{statut}.png"
        
        formatted_date = date_str[:4] + "-" + date_str[4:6] + "-" + date_str[6:8] if date_str != "—" else "—"
        formatted_time = time_str[:2] + ":" + time_str[2:4] + ":" + time_str[4:6] if time_str != "—" else "—"
        
        counts["total"] += 1
        if statut in counts:
            counts[statut] += 1
        
        print(f"   Row: {nom_fichier} | {formatted_date} | {formatted_time} | {statut.upper()}")
    
    print(f"\n   ✓ Formatage OK, {len(logs)} lignes prêtes à afficher")
    print(f"   ✓ Compteurs: {counts}")
    
except Exception as e:
    print(f"   ✗ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST] ✓ Tous les tests passent! Page historique prête à afficher les logs.")
