#!/usr/bin/env python3
"""
Entraînement avec dossier de photos (multiple images par utilisateur)
"""
import cv2
import os
import numpy as np
from recognition.detector import (
    charger_detecteur,
    detecter_visages,
    egaliser_eclairage_gris,
    extraire_roi,
)
from database.db_manager import get_tous_utilisateurs

MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "lbph_model.yml")

def collecter_images_labels_avec_dossiers():
    """
    Collecte les images depuis:
    1. Les photos principales (utilisateurs)
    2. Les dossiers dans faces/ (multi-photos)
    """
    detecteur = charger_detecteur()
    images = []
    labels = []
    utilisateurs = get_tous_utilisateurs()

    for user in utilisateurs:
        user_id = user["id"]
        nom_user = f"{user['prenom']}_{user['nom']}".lower().replace(" ", "_")
        
        # ─── Photo principale ───
        photo_path = user["photo_path"]
        if photo_path and os.path.exists(photo_path):
            try:
                img = cv2.imread(photo_path)
                if img is not None:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    gray = egaliser_eclairage_gris(gray)
                    visages = detecter_visages(gray, detecteur)
                    rois = extraire_roi(gray, visages)
                    for roi in rois:
                        images.append(roi)
                        labels.append(user_id)
                    print(f"  ✓ Photo principale: {user['prenom']} {user['nom']} ({len(rois)} visages)")
            except Exception as e:
                print(f"  ✗ Erreur photo principale: {e}")
        
        # ─── Dossier avec multiples photos ───
        dossier = os.path.join("faces", nom_user)
        if os.path.isdir(dossier):
            for filename in os.listdir(dossier):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                    filepath = os.path.join(dossier, filename)
                    try:
                        img = cv2.imread(filepath)
                        if img is not None:
                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            gray = egaliser_eclairage_gris(gray)
                            visages = detecter_visages(gray, detecteur)
                            rois = extraire_roi(gray, visages)
                            for roi in rois:
                                images.append(roi)
                                labels.append(user_id)
                        print(f"    ✓ {filename} ({len(rois)} visages)")
                    except Exception as e:
                        print(f"    ✗ Erreur {filename}: {e}")

    return images, labels

def entrainer_modele_complet():
    """Entraîne avec toutes les photos disponibles."""
    print("="*80)
    print("COLLECTE DES IMAGES D'ENTRAÎNEMENT")
    print("="*80)
    print("\nPhotos en train de charger...\n")
    
    images, labels = collecter_images_labels_avec_dossiers()
    
    print(f"\n{'='*80}")
    print(f"TOTAL: {len(images)} visages collectés")
    print(f"{'='*80}\n")
    
    if len(images) < 2:
        print("✗ Pas assez d'images (minimum 2)")
        return False
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    # Entraîner avec paramètres optimisés
    modele = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8,
    )
    
    print("Entraînement du modèle LBPH...")
    modele.train(images, np.array(labels))
    modele.save(MODEL_PATH)
    
    print(f"✓ Modèle entraîné et sauvegardé: {MODEL_PATH}")
    print(f"  - {len(images)} images")
    print(f"  - {len(set(labels))} utilisateurs")
    return True

if __name__ == "__main__":
    entrainer_modele_complet()
