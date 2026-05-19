import cv2
import numpy as np
import os

DELIMITER = "###END###"   # marqueur de fin du message caché

def texte_en_bits(texte: str) -> str:
    """Convertit une chaîne en suite de bits (8 bits par caractère UTF-8)."""
    return ''.join(format(byte, '08b') for byte in texte.encode('utf-8'))

def bits_en_texte(bits: str) -> str:
    """Reconvertit une suite de bits en chaîne UTF-8."""
    chars = [bits[i:i+8] for i in range(0, len(bits), 8)]
    return ''.join(chr(int(b, 2)) for b in chars if len(b) == 8)

def encoder(image_path: str, message: str, output_path: str) -> bool:
    """
    Cache 'message' dans l'image via LSB (1 bit par canal R/G/B).
    Sauvegarde le résultat dans output_path.
    Retourne True si succès, False sinon.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"[WATERMARK] Image introuvable : {image_path}")
        return False

    message_complet = message + DELIMITER
    bits = texte_en_bits(message_complet)
    n_bits = len(bits)

    hauteur, largeur, canaux = img.shape
    capacite = hauteur * largeur * canaux  # 1 bit par canal

    if n_bits > capacite:
        print(f"[WATERMARK] Message trop long ({n_bits} bits > capacité {capacite}).")
        return False

    try:
        flat = img.flatten().astype(np.uint8)
        for i, bit in enumerate(bits):
            bit_int = np.uint8(int(bit))
            flat[i] = np.uint8((flat[i] & np.uint8(254)) | bit_int)   # remplace le LSB (254 = 0xFE)

        img_tatouee = flat.reshape(img.shape).astype(np.uint8)
    except Exception as e:
        print(f"[WATERMARK] Erreur lors de l'encodage : {e}")
        return False
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    cv2.imwrite(output_path, img_tatouee)
    print(f"[WATERMARK] Image tatouee -> {output_path}")
    return True

def decoder(image_path: str) -> str | None:
    """
    Extrait le message caché dans une image tatouée par LSB.
    Retourne le message (str) ou None si aucun tatouage trouvé.
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"[WATERMARK] Image introuvable : {image_path}")
            return None

        flat = img.flatten().astype(np.uint8)
        bits = ''.join(str(int(pixel) & 1) for pixel in flat)
        texte = bits_en_texte(bits)

        if DELIMITER in texte:
            message = texte.split(DELIMITER)[0]
            print(f"[WATERMARK] Message extrait : {message}")
            return message

        print("[WATERMARK] Aucun tatouage LSB détecté.")
        return None
    except Exception as e:
        print(f"[WATERMARK] Erreur lors du décodage : {e}")
        return None