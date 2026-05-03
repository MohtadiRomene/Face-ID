#!/usr/bin/env python3
"""
Test complet des 3 scénarios d'utilisation de BiometriX
"""
import os
import sys
import numpy as np
import cv2
from database.db_manager import (
    init_db, ajouter_utilisateur, get_utilisateur_par_id, 
    get_tous_logs, get_statistiques_logs, supprimer_log
)
from watermark.log_manager import sauvegarder_log_tatatoue, verifier_log

print("="*80)
print("TEST COMPLET: 3 SCÉNARIOS DE RECONNAISSANCE FACIALE")
print("="*80)

# ── Préparation ────────────────────────────────────────────────────────────
print("\n[SETUP] Préparation...")

# Nettoyer les anciens logs
if os.path.exists('logs'):
    import shutil
    shutil.rmtree('logs')
print("  ✓ Dossier logs nettoyé")

# Initialiser BD
init_db()
print("  ✓ BD initialisée")

# Ajouter un utilisateur non autorisé pour le scénario 2
try:
    uid2 = ajouter_utilisateur("Dupont", "Jean", role="employe", autorise=0)
    print(f"  ✓ Utilisateur non autorisé créé: ID={uid2}")
except:
    uid2 = 2
    print(f"  ! Utilisateur non autorisé ID={uid2} existant")

# Créer image test
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(test_frame, "TEST SCENARIO", (150, 240), 
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

# ── SCÉNARIO 1: Utilisateur autorisé ───────────────────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 1: UTILISATEUR AUTORISÉ → Accès enregistré + tatoué")
print("="*80)

try:
    user_id = 1
    user = get_utilisateur_par_id(user_id)
    print(f"\n[USER] ID={user_id} | {user['prenom']} {user['nom']} | Autorisé={user['autorise']}")
    
    if user["autorise"] == 1:
        statut = "autorise"
        print(f"[STATUS] ✓ Utilisateur autorisé")
    else:
        statut = "refuse"
        print(f"[STATUS] ✗ Utilisateur connu mais non autorisé")
    
    nom = f"{user['prenom']} {user['nom']}"
    confiance = 48.5  # Score LBPH bas = bon match
    
    # Sauvegarder le log
    print(f"[LOG] Sauvegarde: user_id={user_id}, statut={statut}, confiance={confiance}")
    image_path = sauvegarder_log_tatatoue(test_frame, user_id, statut, nom, confiance)
    print(f"[SAVED] ✓ Image tatuée: {image_path}")
    
    # Vérifier l'enregistrement en BD
    logs = get_tous_logs()
    last_log = logs[0]
    print(f"[BD] ✓ Log en base: ID={last_log['id']}, statut={last_log['statut']}, confiance={last_log['confiance']}")
    
    # Vérifier le watermark
    watermark_info = verifier_log(image_path)
    if watermark_info:
        print(f"[WATERMARK] ✓ Vérifié: user_id={watermark_info.get('user_id')}, statut={watermark_info.get('statut')}")
    else:
        print(f"[WATERMARK] ! Non trouvé ou dégradé")
    
    print("\n✓ SCÉNARIO 1: SUCCÈS")
    
except Exception as e:
    print(f"\n✗ SCÉNARIO 1: ERREUR - {e}")
    import traceback
    traceback.print_exc()

# ── SCÉNARIO 2: Utilisateur connu mais non autorisé ────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 2: UTILISATEUR CONNU NON AUTORISÉ → Alerte + log tatoué")
print("="*80)

try:
    user_id = uid2
    user = get_utilisateur_par_id(user_id)
    print(f"\n[USER] ID={user_id} | {user['prenom']} {user['nom']} | Autorisé={user['autorise']}")
    
    if user["autorise"] == 1:
        statut = "autorise"
        print(f"[STATUS] ✓ Utilisateur autorisé")
    else:
        statut = "refuse"
        print(f"[ALERT] ⚠️  UTILISATEUR BLOQUÉ - Accès refusé")
    
    nom = f"{user['prenom']} {user['nom']} (bloqué)"
    confiance = 52.3  # Score acceptable mais utilisateur bloqué
    
    # Sauvegarder le log
    print(f"[LOG] Sauvegarde: user_id={user_id}, statut={statut}, confiance={confiance}")
    image_path = sauvegarder_log_tatatoue(test_frame, user_id, statut, nom, confiance)
    print(f"[SAVED] ✓ Image tatuée: {image_path}")
    
    # Vérifier l'enregistrement en BD
    logs = get_tous_logs()
    last_log = logs[0]
    print(f"[BD] ✓ Log en base: ID={last_log['id']}, statut={last_log['statut']}, nom={last_log['nom']}")
    
    # Vérifier le watermark
    watermark_info = verifier_log(image_path)
    if watermark_info:
        print(f"[WATERMARK] ✓ Vérifié: user_id={watermark_info.get('user_id')}, statut={watermark_info.get('statut')}")
    
    print("\n✓ SCÉNARIO 2: SUCCÈS")
    
except Exception as e:
    print(f"\n✗ SCÉNARIO 2: ERREUR - {e}")
    import traceback
    traceback.print_exc()

# ── SCÉNARIO 3: Imposteur (visage inconnu) ─────────────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 3: IMPOSTEUR (INCONNU) → Alarme + capture + log tatoué")
print("="*80)

try:
    user_id = 0  # Imposteur/Inconnu
    statut = "imposteur"
    nom = "IMPOSTEUR DÉTECTÉ"
    confiance = 156.8  # Score très mauvais = imposeur
    
    print(f"\n[ALARM] 🚨 IMPOSTEUR DÉTECTÉ!")
    print(f"[USER] ID={user_id} | Visage inconnu | Confiance={confiance}")
    print(f"[STATUS] ✘ Seuil de confiance dépassé (>100)")
    
    # Sauvegarder le log avec capture
    print(f"[LOG] Sauvegarde capture + metadata: user_id={user_id}, statut={statut}, confiance={confiance}")
    image_path = sauvegarder_log_tatatoue(test_frame, user_id, statut, nom, confiance)
    print(f"[CAPTURE] ✓ Capture enregistrée: {image_path}")
    
    # Vérifier l'enregistrement en BD
    logs = get_tous_logs()
    last_log = logs[0]
    print(f"[BD] ✓ Log en base: ID={last_log['id']}, statut={last_log['statut']}, confiance={last_log['confiance']}")
    
    # Vérifier le watermark
    watermark_info = verifier_log(image_path)
    if watermark_info:
        print(f"[WATERMARK] ✓ Vérifié: user_id={watermark_info.get('user_id')}, statut={watermark_info.get('statut')}")
    
    print("\n✓ SCÉNARIO 3: SUCCÈS")
    
except Exception as e:
    print(f"\n✗ SCÉNARIO 3: ERREUR - {e}")
    import traceback
    traceback.print_exc()

# ── Vérification finale ────────────────────────────────────────────────────
print("\n" + "="*80)
print("VÉRIFICATION FINALE")
print("="*80)

try:
    logs = get_tous_logs()
    stats = get_statistiques_logs()
    
    print(f"\n[STATISTIQUES]")
    print(f"  Total de logs           : {stats['total']} (attendu: 3)")
    print(f"  Accès autorisés         : {stats['autorise']} (attendu: 1)")
    print(f"  Accès refusés           : {stats['refuse']} (attendu: 1)")
    print(f"  Imposteurs détectés     : {stats['imposteur']} (attendu: 1)")
    
    print(f"\n[FICHIERS PNG]")
    if os.path.exists('logs'):
        files = [f for f in os.listdir('logs') if f.endswith('.png')]
        print(f"  Fichiers enregistrés    : {len(files)} (attendu: 3)")
        for f in sorted(files):
            print(f"    - {f}")
    else:
        print(f"  ✗ Dossier logs n'existe pas")
    
    # Vérifier que chaque log a un watermark
    print(f"\n[WATERMARKS]")
    watermark_count = 0
    for log in logs:
        image_path = log.get('image_path')
        if image_path and os.path.exists(image_path):
            watermark_info = verifier_log(image_path)
            if watermark_info:
                watermark_count += 1
                print(f"  ✓ {log['nom']:30} | watermark OK")
            else:
                print(f"  ! {log['nom']:30} | watermark dégradé")
    
    print(f"  Watermarks vérifiés     : {watermark_count}/{len(logs)}")
    
    # Résumé final
    print("\n" + "="*80)
    if stats['total'] == 3 and stats['autorise'] == 1 and stats['refuse'] == 1 and stats['imposteur'] == 1:
        print("✅ TOUS LES SCÉNARIOS VALIDÉS AVEC SUCCÈS!")
        print("="*80)
    else:
        print("⚠️  RÉSULTATS PARTIELS - Vérifier les logs")
        print("="*80)
        
except Exception as e:
    print(f"✗ Erreur lors de la vérification finale: {e}")
    import traceback
    traceback.print_exc()
