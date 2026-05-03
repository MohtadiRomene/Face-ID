#!/usr/bin/env python3
"""
Simulation du rendu final dans page_historique.
"""
from database.db_manager import get_tous_logs, get_statistiques_logs

print("="*80)
print("SIMULATION: CE QUE VERRA L'UTILISATEUR DANS L'ONGLET 'HISTORIQUE'")
print("="*80)

# Récupérer les logs
logs = get_tous_logs()
stats = get_statistiques_logs()

print("\n[TABLEAU DES LOGS]")
print("-" * 80)
print(f"{'FICHIER':<40} {'DATE':<12} {'HEURE':<10} {'STATUT':<10}")
print("-" * 80)

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
    
    # Couleur pour le statut
    colors = {
        "autorise": "\033[92m",     # vert
        "refuse": "\033[93m",       # jaune
        "imposteur": "\033[91m"     # rouge
    }
    color_end = "\033[0m"
    
    status_colored = f"{colors.get(statut, '')}{statut.upper():<10}{color_end}"
    
    print(f"{nom_fichier:<40} {formatted_date:<12} {formatted_time:<10} {status_colored}")
    
    counts["total"] += 1
    if statut in counts:
        counts[statut] += 1

print("-" * 80)

print("\n[STATISTIQUES GLOBALES]")
print("-" * 80)
stat_labels = {
    "total": "Total de logs",
    "autorise": "Accès autorisés",
    "refuse": "Accès refusés",
    "imposteur": "Imposteurs"
}
for key, label in stat_labels.items():
    print(f"{label:<30} : {counts[key]}")

print("-" * 80)
print("\n✓ Historique complet affiché avec succès!")
