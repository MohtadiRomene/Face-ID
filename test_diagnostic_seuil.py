#!/usr/bin/env python3
"""
Diagnostic: Vérifier les scores de confiance réels
"""
import os
import cv2
import numpy as np
from recognition.detector import (
    charger_detecteur,
    detecter_visages,
    egaliser_eclairage_gris,
    extraire_roi,
)
from recognition.trainer import charger_modele
from recognition.recognizer import SEUIL_AUTORISE, SEUIL_INCONNU
from database.db_manager import get_tous_utilisateurs

print("="*80)
print("DIAGNOSTIC - VÉRIFICATION DES SCORES DE CONFIANCE")
print("="*80)

try:
    detecteur = charger_detecteur()
    modele = charger_modele()
    print("✓ Modèle chargé\n")
except Exception as e:
    print(f"✗ Erreur lors du chargement: {e}")
    exit(1)

# Tester avec chaque utilisateur
utilisateurs = get_tous_utilisateurs()

for user in utilisateurs:
    print(f"\n{'='*80}")
    print(f"UTILISATEUR: {user['prenom']} {user['nom']} (ID={user['id']})")
    print(f"Photo: {user['photo_path']}")
    print(f"Autorisé: {user['autorise']}")
    print(f"{'='*80}")
    
    photo_path = user['photo_path']
    
    if not photo_path or not os.path.exists(photo_path):
        print(f"✗ Photo introuvable: {photo_path}")
        continue
    
    # Charger la photo
    img = cv2.imread(photo_path)
    if img is None:
        print(f"✗ Impossible de lire la photo")
        continue
    
    print(f"✓ Photo chargée: {img.shape}")
    
    # Détecter le visage
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = egaliser_eclairage_gris(gray)
    visages = detecter_visages(gray, detecteur)
    
    if len(visages) == 0:
        print(f"✗ Aucun visage détecté dans la photo !")
        continue
    
    print(f"✓ {len(visages)} visage(s) détecté(s)")
    
    # Extraire ROI
    rois = extraire_roi(gray, visages)
    
    # Prédire avec le modèle
    for i, roi in enumerate(rois):
        label, confiance = modele.predict(roi)
        
        print(f"\n  Visage {i+1}:")
        print(f"    Label prédit: {label}")
        print(f"    Confiance: {confiance:.2f}")
        
        # Interpréter (même logique que recognition.recognizer.analyser_frame)
        if confiance < SEUIL_AUTORISE:
            print(f"    → zone reconnaissance (confiance < {SEUIL_AUTORISE})")
        elif confiance < SEUIL_INCONNU:
            print(f"    → ⚠️  REFUS / inconnu (faible confiance)")
        else:
            print(f"    → 🚨 IMPOSTEUR (confiance ≥ {SEUIL_INCONNU})")

print("\n" + "="*80)
print("SEUILS ACTUELS (recognition.recognizer):")
print(f"  SEUIL_AUTORISE = {SEUIL_AUTORISE} (match si < seuil + utilisateur autorisé)")
print(f"  SEUIL_INCONNU  = {SEUIL_INCONNU} (imposteur si ≥ seuil)")
print("="*80)
