import cv2
from database.db_manager   import init_db, ajouter_utilisateur
from recognition.trainer   import entrainer_modele
from recognition.detector  import charger_detecteur, detecter_visages

# ── 1. Initialiser la DB ───────────────────────────────────────────
init_db()

# ── 2. Ajouter un utilisateur avec sa photo ────────────────────────
# Remplacez "faces/ahmed.jpg" par un vrai fichier photo
user_id = ajouter_utilisateur("romene", "mohtadi",
                               photo_path="faces/mohtadi.png",
                               role="admin", autorise=1)

# ── 3. Entraîner le modèle ─────────────────────────────────────────
entrainer_modele()

# ── 4. Tester la détection sur une image ──────────────────────────
img = cv2.imread("faces/mohtadi.png")
if img is not None:
    detecteur = charger_detecteur()
    gray      = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    visages   = detecter_visages(gray, detecteur)
    print(f"[TEST] Visages détectés : {len(visages)}")

    for (x, y, w, h) in visages:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("Test détection", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("[TEST] Image introuvable — placez une photo dans faces/mohtadi.png")

# ── 5. Lancer la webcam en temps réel ─────────────────────────────
from recognition.recognizer import lancer_reconnaissance
lancer_reconnaissance()   # décommentez quand le modèle est prêt