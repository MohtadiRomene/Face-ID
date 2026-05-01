import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading

class TabCamera(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app      = app
        self.cap      = None
        self.actif    = False
        self._detecteur = None
        self._modele    = None
        self._construire_ui()

    def _construire_ui(self):
        tk.Label(self, text="Reconnaissance faciale en direct",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 4))

        # Canvas pour afficher le flux vidéo
        self.canvas = tk.Canvas(self, width=640, height=480, bg="black")
        self.canvas.pack(padx=10, pady=5)

        # Cadre statut
        self.statut_cam = tk.StringVar(value="Caméra arrêtée")
        tk.Label(self, textvariable=self.statut_cam,
                 font=("Helvetica", 10), fg="#e74c3c").pack(pady=2)

        # Boutons
        frame_btn = tk.Frame(self)
        frame_btn.pack(pady=6)
        self.btn_start = tk.Button(frame_btn, text="Démarrer la caméra",
                                    command=self.demarrer_camera,
                                    bg="#27ae60", fg="white", width=18)
        self.btn_start.pack(side=tk.LEFT, padx=6)
        self.btn_stop = tk.Button(frame_btn, text="Arrêter",
                                   command=self.arreter_camera,
                                   bg="#e74c3c", fg="white", width=10,
                                   state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=6)

    def demarrer_camera(self):
        try:
            from recognition.detector import charger_detecteur
            from recognition.trainer  import charger_modele
            self._detecteur = charger_detecteur()
            self._modele    = charger_modele()
        except FileNotFoundError as e:
            from tkinter import messagebox
            messagebox.showerror("Modèle introuvable",
                                  f"{e}\nEntraînez d'abord le modèle.")
            return

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            from tkinter import messagebox
            messagebox.showerror("Webcam", "Impossible d'ouvrir la webcam.")
            return

        self.actif = True
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.statut_cam.set("Caméra active — reconnaissance en cours…")
        self.app.set_statut("Caméra démarrée.")
        self._boucle_video()

    def _boucle_video(self):
        if not self.actif:
            return

        ret, frame = self.cap.read()
        if ret:
            from recognition.recognizer import analyser_frame
            from watermark.log_manager  import sauvegarder_log_tatatoue

            frame, resultats = analyser_frame(frame, self._detecteur, self._modele)

            for r in resultats:
                if r["statut"] in ("refuse", "imposteur"):
                    threading.Thread(
                        target=sauvegarder_log_tatatoue,
                        args=(frame.copy(), r["user_id"] or 0,
                              r["statut"], r["nom"]),
                        daemon=True
                    ).start()

            # Conversion BGR → RGB → PhotoImage
            img_rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil  = Image.fromarray(img_rgb)
            img_pil  = img_pil.resize((640, 480))
            self._photo = ImageTk.PhotoImage(img_pil)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self._photo)

        # Rappel toutes les 30ms (~33 fps)
        self.after(30, self._boucle_video)

    def arreter_camera(self):
        self.actif = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.canvas.delete("all")
        self.statut_cam.set("Caméra arrêtée")
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.app.set_statut("Caméra arrêtée.")