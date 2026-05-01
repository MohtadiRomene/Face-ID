import cv2
from recognition.detector import charger_detecteur, detecter_visages, extraire_roi, dessiner_rectangles
from recognition.trainer  import charger_modele
from database.db_manager  import get_utilisateur_par_id
from watermark.log_manager import sauvegarder_log_tatatoue

# Seuils de confiance LBPH (plus la valeur est BASSE, plus le match est bon)
SEUIL_AUTORISE  = 60   # < 60  → utilisateur reconnu
SEUIL_INCONNU   = 100  # > 100 → imposteur (visage inconnu)

def analyser_frame(frame, detecteur, modele):
    """
    Analyse une frame vidéo :
    - Détecte les visages
    - Prédit l'identité via LBPH
    - Retourne la liste des résultats [{user_id, statut, confiance, rect}]
    """
    gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    visages = detecter_visages(gray, detecteur)
    rois    = extraire_roi(gray, visages)
    resultats = []

    for i, roi in enumerate(rois):
        label, confiance = modele.predict(roi)

        if confiance < SEUIL_AUTORISE:
            user = get_utilisateur_par_id(label)
            if user and user["autorise"] == 1:
                statut  = "autorise"
                couleur = (0, 220, 100)     # vert
                nom     = f"{user['prenom']} {user['nom']}"
            else:
                statut  = "refuse"
                couleur = (0, 100, 255)     # orange
                nom     = f"{user['prenom']} {user['nom']} (bloqué)"

        elif confiance < SEUIL_INCONNU:
            statut  = "refuse"
            couleur = (0, 100, 255)
            label   = None
            nom     = "Inconnu (faible confiance)"

        else:
            statut  = "imposteur"
            couleur = (0, 0, 255)           # rouge
            label   = None
            nom     = "IMPOSTEUR"

        # Affichage sur la frame
        x, y, w, h = visages[i]
        cv2.rectangle(frame, (x, y), (x + w, y + h), couleur, 2)
        texte = f"{nom}  [{confiance:.1f}]"
        cv2.putText(frame, texte, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 1)

        resultats.append({
            "user_id":   label,
            "statut":    statut,
            "confiance": confiance,
            "rect":      visages[i],
            "nom":       nom
        })

    return frame, resultats

def lancer_reconnaissance():
    """
    Lance la reconnaissance faciale en temps réel via la webcam.
    Appuyez sur Q pour quitter.
    """
    detecteur = charger_detecteur()
    modele    = charger_modele()
    cap       = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[RECOG] Impossible d'ouvrir la webcam.")
        return

    print("[RECOG] Reconnaissance active — appuyez sur Q pour quitter.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, resultats = analyser_frame(frame, detecteur, modele)

        for r in resultats:
            if r["statut"] in ("refuse", "imposteur"):
                sauvegarder_log_tatatoue(
                    frame,
                    user_id = r["user_id"] or 0,
                    statut  = r["statut"],
                    nom     = r["nom"]
                )

        for r in resultats:
            print(f"  → {r['nom']} | {r['statut']} | confiance={r['confiance']:.1f}")

        cv2.imshow("Biometrie — Reconnaissance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()