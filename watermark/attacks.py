"""
Attaques sur images pour tester la robustesse du watermark LSB.
Chaque attaque simule une modification malveillante ou involontaire.
"""
import os
import cv2
import numpy as np
from typing import Callable

from watermark.log_manager import verifier_log

LOGS_ATTACKS_DIR = os.path.join("logs", "attacks")

# type_attaque -> (libelle affiche, fonction)
AttaqueFn = Callable[[np.ndarray], np.ndarray]

ATTACKS: dict[str, tuple[str, AttaqueFn]] = {}


def _register(name: str, label: str):
    def decorator(fn: AttaqueFn) -> AttaqueFn:
        ATTACKS[name] = (label, fn)
        return fn
    return decorator


@_register("jpeg", "Compression JPEG (qualite 50)")
def _attaque_jpeg(img: np.ndarray) -> np.ndarray:
    os.makedirs(LOGS_ATTACKS_DIR, exist_ok=True)
    tmp = os.path.abspath(os.path.join(LOGS_ATTACKS_DIR, "_tmp_jpeg.jpg"))
    if not cv2.imwrite(tmp, img, [cv2.IMWRITE_JPEG_QUALITY, 50]):
        return img
    out = cv2.imread(tmp, cv2.IMREAD_COLOR)
    if os.path.exists(tmp):
        os.remove(tmp)
    if out is None:
        raise RuntimeError("Echec lecture apres compression JPEG")
    return out


@_register("blur", "Flou gaussien")
def _attaque_blur(img: np.ndarray) -> np.ndarray:
    return cv2.GaussianBlur(img, (9, 9), 0)


@_register("noise", "Bruit aleatoire")
def _attaque_noise(img: np.ndarray) -> np.ndarray:
    noise = np.random.randint(-25, 25, img.shape, dtype=np.int16)
    return np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)


@_register("crop", "Recadrage 80 % puis agrandissement")
def _attaque_crop(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    margin_x = int(w * 0.1)
    margin_y = int(h * 0.1)
    cropped = img[margin_y:h - margin_y, margin_x:w - margin_x]
    return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)


@_register("brightness", "Variation de luminosite (+40)")
def _attaque_brightness(img: np.ndarray) -> np.ndarray:
    return np.clip(img.astype(np.int16) + 40, 0, 255).astype(np.uint8)


@_register("resize", "Redimensionnement 50 % puis retour")
def _attaque_resize(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    small = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)


@_register("rotate", "Rotation legere (5 degres)")
def _attaque_rotate(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, 5.0, 1.0)
    return cv2.warpAffine(
        img, matrix, (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def lister_attaques() -> list[tuple[str, str]]:
    """Retourne [(cle, libelle), ...] pour les menus."""
    return [(k, v[0]) for k, v in ATTACKS.items()]


def appliquer_attaque(
    image_path: str,
    type_attaque: str,
    output_path: str | None = None,
) -> str:
    """
    Applique une attaque sur une image et sauvegarde le resultat.

    Retourne le chemin du fichier attaque.
    """
    if type_attaque not in ATTACKS:
        raise ValueError(
            f"Attaque inconnue : {type_attaque}. "
            f"Disponibles : {', '.join(ATTACKS)}"
        )

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    _, fn = ATTACKS[type_attaque]
    img_attaque = fn(img)

    os.makedirs(LOGS_ATTACKS_DIR, exist_ok=True)
    if output_path is None:
        base = os.path.splitext(os.path.basename(image_path))[0]
        output_path = os.path.join(
            LOGS_ATTACKS_DIR,
            f"{base}_attaque_{type_attaque}.png",
        )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cv2.imwrite(output_path, img_attaque)
    print(f"[ATTAQUE] {type_attaque} -> {output_path}")
    return output_path


def verifier_apres_attaque(chemin_attaque: str) -> dict:
    """
    Verifie le watermark LSB sur une image attaquee.
    Retourne {valide, infos, message_extrait}.
    """
    infos = verifier_log(chemin_attaque)
    return {
        "valide": infos is not None,
        "infos": infos,
    }


def tester_toutes_attaques(image_path: str) -> list[dict]:
    """
    Applique chaque attaque puis verifie le watermark.
    Utile en ligne de commande ou pour rapports.
    """
    resultats = []
    for cle, (libelle, _) in ATTACKS.items():
        try:
            chemin = appliquer_attaque(image_path, cle)
            verif = verifier_apres_attaque(chemin)
            resultats.append({
                "attaque": cle,
                "libelle": libelle,
                "fichier": chemin,
                "watermark_ok": verif["valide"],
                "infos": verif["infos"],
            })
        except Exception as e:
            resultats.append({
                "attaque": cle,
                "libelle": libelle,
                "fichier": None,
                "watermark_ok": False,
                "erreur": str(e),
            })
    return resultats
