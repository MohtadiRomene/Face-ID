import cv2
import os
import numpy as np
from database.db_manager import get_tous_utilisateurs

MODELS_DIR = "models"
MODEL_PATH = os.path.join(MODELS_DIR, "lbph_model.yml")

# Distance LBPH max pour accepter un visage (doit rester aligné avec recognizer.py)
SEUIL_LBPH = 62


def _ajouter_rois_depuis_image(img_path, user_id, detecteur, images, labels, nom_affiche):
    """Extrait les visages d'une image et les ajoute aux listes d'entraînement."""
    from recognition.detector import (
        detecter_visages,
        egaliser_eclairage_gris,
        extraire_roi,
        selectionner_visage_principal,
    )

    img = cv2.imread(img_path)
    if img is None:
        return 0

    gray = egaliser_eclairage_gris(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    visages = selectionner_visage_principal(detecter_visages(gray, detecteur))
    rois = extraire_roi(gray, visages)
    for roi in rois:
        images.append(roi)
        labels.append(user_id)
    if rois:
        print(
            f"[TRAINER] {len(rois)} visage(s) - {nom_affiche} "
            f"(label={user_id}) <- {img_path}"
        )
    return len(rois)


def collecter_images_labels():
    """
    Collecte les visages depuis la photo principale de chaque utilisateur
    et depuis faces/<prenom>_<nom>/ si présent (multi-photos).
    """
    from recognition.detector import charger_detecteur

    detecteur = charger_detecteur()
    images = []
    labels = []

    for user in get_tous_utilisateurs():
        user_id = user["id"]
        nom_user = f"{user['prenom']}_{user['nom']}".lower().replace(" ", "_")
        nom_affiche = f"{user['prenom']} {user['nom']}"

        photo_path = user.get("photo_path")
        if photo_path and os.path.exists(photo_path):
            _ajouter_rois_depuis_image(
                photo_path, user_id, detecteur, images, labels, nom_affiche,
            )
        else:
            print(f"[TRAINER] Aucune photo pour {nom_affiche} — ignoré.")

        dossier = os.path.join("faces", nom_user)
        if os.path.isdir(dossier):
            for filename in sorted(os.listdir(dossier)):
                if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                    _ajouter_rois_depuis_image(
                        os.path.join(dossier, filename),
                        user_id,
                        detecteur,
                        images,
                        labels,
                        nom_affiche,
                    )

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

    # Paramètres proches des défauts OpenCV : meilleure généralisation éclairage / pose
    modele = cv2.face.LBPHFaceRecognizer_create(
        radius=1,
        neighbors=8,
        grid_x=8,
        grid_y=8,
    )
    modele.train(images, np.array(labels))
    modele.setThreshold(SEUIL_LBPH)
    modele.save(MODEL_PATH)
    print(
        f"[TRAINER] Modele entraine ({len(images)} visages, "
        f"seuil LBPH={SEUIL_LBPH}) -> {MODEL_PATH}"
    )
    return True


def charger_modele():
    """Charge le modèle LBPH pré-entraîné depuis le disque."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Modèle introuvable : {MODEL_PATH} — lancez d'abord entrainer_modele()"
        )
    modele = cv2.face.LBPHFaceRecognizer_create()
    modele.read(MODEL_PATH)
    modele.setThreshold(SEUIL_LBPH)
    print(f"[TRAINER] Modèle chargé depuis {MODEL_PATH} (seuil LBPH={SEUIL_LBPH})")
    return modele