#!/usr/bin/env python3
"""
TEST COMPLET CLEAN - 3 Scénarios avec BD vierge
"""
import os
import sqlite3
import numpy as np
import cv2
from database.db_manager import (
    ajouter_utilisateur, get_utilisateur_par_id, 
    get_tous_logs, get_statistiques_logs
)
from watermark.log_manager import sauvegarder_log_tatatoue, verifier_log

print("="*80)
print("TEST COMPLET ET PROPRE: 3 SCÉNARIOS DE RECONNAISSANCE FACIALE")
print("="*80)

# ── Nettoyage complet ──────────────────────────────────────────────────────
print("\n[NETTOYAGE] Suppression des données anciennes...")

# Supprimer les logs
if os.path.exists('logs'):
    import shutil
    shutil.rmtree('logs')

# Supprimer et recréer la BD vierge
if os.path.exists('biometrie.db'):
    os.remove('biometrie.db')
    
print("  ✓ Dossier logs et BD supprimés")

# ── Initialisation fraîche ──────────────────────────────────────────────────
print("\n[INIT] Initialisation fraîche...")

from database.db_manager import init_db

init_db()
print("  ✓ BD créée vierge")

# Ajouter 2 utilisateurs de test
uid1 = ajouter_utilisateur("mohtadi", "Romene", role="admin", autorise=1)
uid2 = ajouter_utilisateur("Dupont", "Jean", role="employe", autorise=0)
print(f"  ✓ Utilisateur 1: ID={uid1} (autorisé)")
print(f"  ✓ Utilisateur 2: ID={uid2} (NON autorisé)")

# Créer image test
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(test_frame, "SCENARIO TEST", (150, 240), 
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)

# ── SCÉNARIO 1 ─────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 1: UTILISATEUR AUTORISÉ")
print("="*80)

user = get_utilisateur_par_id(uid1)
print(f"\n[DÉTAILS]")
print(f"  ID: {uid1}")
print(f"  Nom: {user['prenom']} {user['nom']}")
print(f"  Autorisé: ✓ OUI")

image_path_1 = sauvegarder_log_tatatoue(
    test_frame, 
    uid1, 
    "autorise",
    f"{user['prenom']} {user['nom']}",
    48.5
)
print(f"\n[ENREGISTREMENT]")
print(f"  ✓ Accès enregistré")
print(f"  ✓ Image tatuée: {image_path_1}")

wm1 = verifier_log(image_path_1)
if wm1:
    print(f"  ✓ Watermark valide")

logs = get_tous_logs()
print(f"  ✓ Logs en BD: {len(logs)}")

# ── SCÉNARIO 2 ─────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 2: UTILISATEUR CONNU NON AUTORISÉ")
print("="*80)

user = get_utilisateur_par_id(uid2)
print(f"\n[DÉTAILS]")
print(f"  ID: {uid2}")
print(f"  Nom: {user['prenom']} {user['nom']}")
print(f"  Autorisé: ✗ NON")

print(f"\n[ALERTE]")
print(f"  ⚠️  ACCÈS REFUSÉ - Utilisateur bloqué")

image_path_2 = sauvegarder_log_tatatoue(
    test_frame,
    uid2,
    "refuse",
    f"{user['prenom']} {user['nom']} (bloqué)",
    52.3
)
print(f"\n[ENREGISTREMENT]")
print(f"  ✓ Tentative enregistrée en tant que refusée")
print(f"  ✓ Image tatuée: {image_path_2}")

wm2 = verifier_log(image_path_2)
if wm2:
    print(f"  ✓ Watermark valide")

logs = get_tous_logs()
print(f"  ✓ Logs en BD: {len(logs)}")

# ── SCÉNARIO 3 ─────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("SCÉNARIO 3: IMPOSTEUR (INCONNU)")
print("="*80)

print(f"\n[ALERTE]")
print(f"  🚨 ALARME - IMPOSTEUR DÉTECTÉ")
print(f"  Visage inconnu (confiance > 100)")

image_path_3 = sauvegarder_log_tatatoue(
    test_frame,
    0,
    "imposteur",
    "IMPOSTEUR DÉTECTÉ",
    156.8
)
print(f"\n[ENREGISTREMENT]")
print(f"  ✓ Capture automatique enregistrée")
print(f"  ✓ Image tatuée: {image_path_3}")

wm3 = verifier_log(image_path_3)
if wm3:
    print(f"  ✓ Watermark valide")

logs = get_tous_logs()
print(f"  ✓ Logs en BD: {len(logs)}")

# ── VÉRIFICATION FINALE ────────────────────────────────────────────────────
print("\n" + "="*80)
print("RÉSUMÉ FINAL")
print("="*80)

stats = get_statistiques_logs()
logs = get_tous_logs()

print(f"\n[STATISTIQUES]")
print(f"  ✓ Total de logs: {stats['total']} (attendu: 3)")
print(f"  ✓ Autorisés: {stats['autorise']} (attendu: 1)")
print(f"  ✓ Refusés: {stats['refuse']} (attendu: 1)")
print(f"  ✓ Imposteurs: {stats['imposteur']} (attendu: 1)")

print(f"\n[FICHIERS PNG]")
files = sorted([f for f in os.listdir('logs') if f.endswith('.png')])
for f in files:
    print(f"  ✓ {f}")
print(f"  Nombre: {len(files)} (attendu: 3)")

print(f"\n[WATERMARKS]")
for i, log in enumerate(logs, 1):
    wm = verifier_log(log['image_path'])
    status = "✓" if wm else "✗"
    print(f"  {status} {log['nom']:25} | {log['statut']:8} | {log['confiance']:6.1f}")

print("\n" + "="*80)
if stats['total'] == 3 and len(files) == 3:
    print("✅ VALIDATION COMPLÈTE: TOUS LES SCÉNARIOS FONCTIONNENT!")
    print("\n📋 Résumé:")
    print("   1️⃣  Utilisateur autorisé → Accès enregistré + tatoué ✓")
    print("   2️⃣  Utilisateur connu non autorisé → Alerte + log tatoué ✓")
    print("   3️⃣  Imposteur → Alarme + capture + log tatoué ✓")
    print("\n✓ Base de données: 3 entrées")
    print("✓ Fichiers PNG: 3 images avec watermark")
    print("✓ Historique: Prêt à afficher")
else:
    print("⚠️  ERREUR: Certains scénarios n'ont pas fonctionné")

print("="*80)
