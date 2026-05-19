import cv2
import os

# Chemin vers le fichier XML du classificateur Haar (inclus avec OpenCV)
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# CLAHE réutilisé (meilleur que equalizeHist sur ROI seul pour contre-jour / faible contraste)
_clahe = None


def egaliser_eclairage_gris(gray):
    """
    Normalise le contraste local (CLAHE) sur toute l'image en niveaux de gris.
    À appliquer avant Haar + extraction ROI, identique à l'entraînement et à la webcam.
    """
    global _clahe
    if _clahe is None:
        _clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return _clahe.apply(gray)

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
    return visages


def selectionner_visage_principal(visages):
    """Garde le plus grand visage (évite les doubles détections Haar)."""
    if len(visages) <= 1:
        return visages
    return [max(visages, key=lambda v: v[2] * v[3])]

def dessiner_rectangles(image, visages, couleur=(0, 255, 0), epaisseur=2):
    """Dessine un rectangle autour de chaque visage détecté."""
    for (x, y, w, h) in visages:
        cv2.rectangle(image, (x, y), (x + w, y + h), couleur, epaisseur)
    return image

def normaliser_roi(roi):
    """CLAHE sur le visage recadré (aligné entraînement / webcam)."""
    global _clahe
    if _clahe is None:
        _clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return _clahe.apply(roi)


def extraire_roi(image_gray, visages, taille=(200, 200)):
    """
    Extrait, redimensionne et normalise chaque ROI.
    L'image globale doit déjà avoir été passée par egaliser_eclairage_gris().
    """
    rois = []
    for (x, y, w, h) in visages:
        roi = image_gray[y:y + h, x:x + w]
        roi = cv2.resize(roi, taille)
        roi = normaliser_roi(roi)
        rois.append(roi)
    return rois