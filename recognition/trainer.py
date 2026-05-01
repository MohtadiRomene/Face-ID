import cv2
import os
import numpy as np
from database.db_manager import get_tous_utilisateurs

MODELS_DIR = "models"
MODEL_PATH  = os.path.join(MODELS_DIR, "lbph_model.yml")

def collecter_images_labels():
    """
    Parcourt le dossier faces/ pour chaque utilisateur enregistré
    et construit les listes images + labels pour l'entraînement.
    """
    from recognition.detector import charger_detecteur, detecter_visages, extraire_roi

    detecteur = charger_detecteur()
    images  = []
    labels  = []
    utilisateurs = get_tous_utilisateurs()

    for user in utilisateurs:
        user_id    = user["id"]
        photo_path = user["photo_path"]

        if not photo_path or not os.path.exists(photo_path):
            print(f"[TRAINER] Aucune photo pour {user['prenom']} {user['nom']} — ignoré.")
            continue

        img = cv2.imread(photo_path)
        if img is None:
            continue

        gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        visages = detecter_visages(gray, detecteur)
        rois    = extraire_roi(gray, visages)

        for roi in rois:
            images.append(roi)
            labels.append(user_id)
            print(f"[TRAINER] Visage ajouté — {user['prenom']} {user['nom']} (label={user_id})")

    return images, labels

def entrainer_modele():
    """
    Entraîne le modèle LBPH et sauvegarde le fichier .yml dans models/.
    """
    images, labels = collecter_images_labels()

    if len(images) < 2:
        print("[TRAINER] Pas assez d'images pour entraîner (minimum 2).")
        return False

    os.makedirs(MODELS_DIR, exist_ok=True)

    modele = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8
    )
    modele.train(images, np.array(labels))
    modele.save(MODEL_PATH)
    print(f"[TRAINER] Modèle entraîné ({len(images)} images) → {MODEL_PATH}")
    return True

def charger_modele():
    """Charge le modèle LBPH pré-entraîné depuis le disque."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH} — lancez d'abord entrainer_modele()")
    modele = cv2.face.LBPHFaceRecognizer_create()
    modele.read(MODEL_PATH)
    print(f"[TRAINER] Modèle chargé depuis {MODEL_PATH}")
    return modele