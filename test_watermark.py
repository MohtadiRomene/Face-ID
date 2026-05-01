import cv2
import numpy as np
from watermark.watermarker import encoder, decoder
from watermark.log_manager  import sauvegarder_log_tatatoue, verifier_log

# ── 1. Créer une image de test (si vous n'avez pas de frame webcam) ─
img_test = np.zeros((480, 640, 3), dtype=np.uint8)
img_test[:] = (50, 100, 150)   # couleur unie bleue
cv2.imwrite("test_input.png", img_test)

# ── 2. Encoder un message ──────────────────────────────────────────
message = "user_id=3|statut=autorise|nom=Ahmed Ben Ali|date=20250101_120000"
succes = encoder("test_input.png", message, "test_output.png")
print(f"Encodage : {'OK' if succes else 'ÉCHEC'}")

# ── 3. Décoder et vérifier ─────────────────────────────────────────
message_extrait = decoder("test_output.png")
print(f"Message extrait : {message_extrait}")
assert message_extrait == message, "ERREUR : le message extrait est différent !"
print("Test LSB réussi — le watermark est invisible et intact.")

# ── 4. Tester avec une vraie frame (simulée ici) ───────────────────
frame_fake = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
chemin_log = sauvegarder_log_tatatoue(frame_fake, user_id=3,
                                       statut="autorise", nom="Ahmed Ben Ali")
print(f"Log sauvegardé : {chemin_log}")

infos = verifier_log(chemin_log)
print(f"Vérification : {infos}")