#!/usr/bin/env python3
"""
Test pour vérifier que page_historique affiche bien les logs.
"""
from database.db_manager import get_tous_logs, get_statistiques_logs

print("[TEST] Vérification des données pour l'historique...\n")

# Récupérer les logs
logs = get_tous_logs()
print(f"Nombre total de logs: {len(logs)}")

# Récupérer les stats
stats = get_statistiques_logs()
print(f"\nStatistiques:")
for key, val in stats.items():
    print(f"  {key}: {val}")

# Simuler ce que page_historique affiche
print(f"\nLogs qui seraient affichés dans l'historique:")
for i, log in enumerate(logs):
    date_heure = log.get("date_heure", "—")
    
    # Extraire date et heure du timestamp
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
    
    print(f"  Row {i+1}:")
    print(f"    Fichier: {nom_fichier}")
    print(f"    Date: {formatted_date}")
    print(f"    Heure: {formatted_time}")
    print(f"    Statut: {statut.upper()}")
    print(f"    Nom: {log.get('nom')}")
    print()

print("[TEST] ✓ Vérification terminée!")
