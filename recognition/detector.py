import cv2
import os

# Chemin vers le fichier XML du classificateur Haar (inclus avec OpenCV)
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def charger_detecteur():
    """Charge le classificateur Haar Cascade."""
    if not os.path.exists(HAAR_PATH):
        raise FileNotFoundError(f"Fichier Haar introuvable : {HAAR_PATH}")
    detecteur = cv2.CascadeClassifier(HAAR_PATH)
    print("[DETECTOR] Haar Cascade chargé.")
    return detecteur

def detecter_visages(image_gray, detecteur, scale=1.1, min_voisins=5, taille_min=(60, 60)):
    """
    Détecte les visages dans une image en niveaux de gris.

    Retourne une liste de tuples (x, y, w, h).
    """
    visages = detecteur.detectMultiScale(
        image_gray,
        scaleFactor=scale,
        minNeighbors=min_voisins,
        minSize=taille_min,
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    if len(visages) == 0:
        return []
    return visages  # array de (x, y, w, h)

def dessiner_rectangles(image, visages, couleur=(0, 255, 0), epaisseur=2):
    """Dessine un rectangle autour de chaque visage détecté."""
    for (x, y, w, h) in visages:
        cv2.rectangle(image, (x, y), (x + w, y + h), couleur, epaisseur)
    return image

def extraire_roi(image_gray, visages, taille=(200, 200)):
    """
    Extrait et redimensionne chaque région d'intérêt (ROI) du visage.
    Retourne une liste d'images en niveaux de gris normalisées.
    """
    rois = []
    for (x, y, w, h) in visages:
        roi = image_gray[y:y + h, x:x + w]
        roi = cv2.resize(roi, taille)
        roi = cv2.equalizeHist(roi)   # améliore le contraste
        rois.append(roi)
    return rois