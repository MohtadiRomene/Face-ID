from database.db_manager import (
    init_db, ajouter_utilisateur, get_tous_utilisateurs,
    ajouter_log, get_logs_recents, ajouter_alerte
)

# 1. Initialiser la base
init_db()

# 2. Ajouter des utilisateurs de test
id1 = ajouter_utilisateur("Ben Ali",  "Ahmed",  role="admin", photo_path="C:\Users\Mohtadi\Desktop\VDSE4422.JPG", autorise=1)
id2 = ajouter_utilisateur("Trabelsi", "Sonia",  role="user",   photo_path="faces/sonia.jpg", autorise=1)
id3 = ajouter_utilisateur("Mejri",    "Khalil", role="user",   photo_path="faces/khalil.jpg", autorise=0)

# 3. Simuler des logs d'accès
log1 = ajouter_log(id1, "autorise",  image_log_path="logs/log_001.png")
log2 = ajouter_log(id2, "autorise",  image_log_path="logs/log_002.png")
log3 = ajouter_log(id3, "refuse",    image_log_path="logs/log_003.png")
log4 = ajouter_log(None,"imposteur", image_log_path="logs/log_004.png")

# 4. Créer des alertes pour les accès refusés
ajouter_alerte(log3, "acces_refuse")
ajouter_alerte(log4, "imposteur")

# 5. Afficher tous les logs
print("\n── Logs récents ──")
for log in get_logs_recents():
    nom = f"{log['prenom']} {log['nom']}" if log['nom'] else "Inconnu"
    print(f"  [{log['date_heure']}] {nom} → {log['statut']}")

print("\n[OK] Test terminé — vérifiez le fichier biometrie.db")