import cv2
import os
import datetime
from watermark.watermarker import encoder, decoder

LOGS_DIR = "logs"

def sauvegarder_log_tatatoue(frame, user_id: int, statut: str, nom: str) -> str:
    """
    Sauvegarde une frame capturée avec un watermark LSB contenant :
    - l'identifiant de l'utilisateur
    - le statut (autorise / refuse / imposteur)
    - la date et l'heure
    Retourne le chemin de l'image sauvegardée.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    horodatage = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nom_fichier = f"{LOGS_DIR}/log_{horodatage}_{statut}.png"

    # Sauvegarde temporaire de la frame brute
    fichier_temp = f"{LOGS_DIR}/_temp_frame.png"
    cv2.imwrite(fichier_temp, frame)

    # Construction du message à cacher
    message = f"user_id={user_id}|statut={statut}|nom={nom}|date={horodatage}"

    # Encodage LSB
    succes = encoder(fichier_temp, message, nom_fichier)
    os.remove(fichier_temp)

    if succes:
        return nom_fichier
    else:
        # Fallback : sauvegarde sans tatouage
        cv2.imwrite(nom_fichier, frame)
        return nom_fichier

def verifier_log(image_path: str) -> dict | None:
    """
    Vérifie l'authenticité d'une image de log en extrayant le watermark.
    Retourne un dict {user_id, statut, nom, date} ou None.
    """
    message = decoder(image_path)
    if message is None:
        return None

    infos = {}
    for paire in message.split('|'):
        if '=' in paire:
            cle, valeur = paire.split('=', 1)
            infos[cle] = valeur
    return infos