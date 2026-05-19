import cv2
from recognition.detector import (
    charger_detecteur,
    detecter_visages,
    egaliser_eclairage_gris,
    extraire_roi,
    selectionner_visage_principal,
)
from recognition.trainer import charger_modele, SEUIL_LBPH
from database.db_manager import get_utilisateur_par_id, get_tous_utilisateurs
from watermark.log_manager import sauvegarder_log_tatatoue

# LBPH OpenCV : distance CHI-SQUARE — plus BAS = meilleur match (pas un pourcentage).
# SEUIL_LBPH est aussi appliqué via model.setThreshold() à l'entraînement / chargement.
SEUIL_AUTORISE = SEUIL_LBPH   # distance LBPH max pour accepter
SEUIL_INCONNU   = 90          # au-dessus → refus (visage non reconnu)
SEUIL_IMPOSTEUR = 120         # ≥ 120 → alerte imposteur

_DISTANCE_REJET = 1e6


def distance_vers_score(distance: float) -> float:
    """Convertit une distance LBPH en score 0–100 % pour l'interface."""
    if distance >= SEUIL_INCONNU or distance > _DISTANCE_REJET:
        return 0.0
    if distance <= 0:
        return 100.0
    return max(0.0, min(100.0, (1.0 - distance / SEUIL_AUTORISE) * 100.0))


def _ids_utilisateurs_connus():
    return {u["id"] for u in get_tous_utilisateurs()}


def classer_prediction(label: int, distance: float):
    """
    Détermine le statut à partir du label LBPH et de la distance.
    Retourne (statut, label_utilisable, nom_affichage, couleur_bgr).
    """
    if label < 0 or distance > _DISTANCE_REJET:
        return "refuse", None, "Inconnu (non enregistré)", (0, 100, 255)

    if distance >= SEUIL_IMPOSTEUR:
        return "imposteur", None, "IMPOSTEUR", (0, 0, 255)

    if distance >= SEUIL_INCONNU:
        return "refuse", None, "Inconnu (visage non reconnu)", (0, 100, 255)

    if distance >= SEUIL_AUTORISE:
        return "refuse", None, "Inconnu (faible correspondance)", (0, 100, 255)

    if label not in _ids_utilisateurs_connus():
        return "refuse", None, "Inconnu (identité invalide)", (0, 100, 255)

    user = get_utilisateur_par_id(label)
    if not user:
        return "refuse", None, "Inconnu (utilisateur absent)", (0, 100, 255)

    nom = f"{user['prenom']} {user['nom']}"
    if user["autorise"] == 1:
        return "autorise", label, nom, (0, 220, 100)

    return "refuse", label, f"{nom} (bloqué)", (0, 100, 255)


def analyser_frame(frame, detecteur, modele):
    """
    Analyse une frame vidéo :
    - Détecte les visages
    - Prédit l'identité via LBPH
    - Retourne la liste des résultats [{user_id, statut, confiance, score_pct, rect}]
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = egaliser_eclairage_gris(gray)
    visages = selectionner_visage_principal(detecter_visages(gray, detecteur))
    rois = extraire_roi(gray, visages)
    resultats = []

    for i, roi in enumerate(rois):
        label, distance = modele.predict(roi)
        statut, label_out, nom, couleur = classer_prediction(label, distance)
        score_pct = distance_vers_score(distance)

        x, y, w, h = visages[i]
        cv2.rectangle(frame, (x, y), (x + w, y + h), couleur, 2)
        texte = f"{nom}  [{score_pct:.0f}%]"
        cv2.putText(
            frame, texte, (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, couleur, 1,
        )

        resultats.append({
            "user_id":   label_out,
            "statut":    statut,
            "confiance": distance,
            "score_pct": score_pct,
            "rect":      visages[i],
            "nom":       nom,
        })

    return frame, resultats


def lancer_reconnaissance():
    """
    Lance la reconnaissance faciale en temps réel via la webcam.
    Appuyez sur Q pour quitter.
    """
    detecteur = charger_detecteur()
    modele = charger_modele()
    cap = cv2.VideoCapture(0)

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
            sauvegarder_log_tatatoue(
                frame,
                user_id=r["user_id"] or 0,
                statut=r["statut"],
                nom=r["nom"],
                confiance=r.get("confiance"),
            )

        for r in resultats:
            print(
                f"  → {r['nom']} | {r['statut']} | "
                f"distance={r['confiance']:.1f} | score={r['score_pct']:.0f}%"
            )

        cv2.imshow("Biometrie — Reconnaissance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
