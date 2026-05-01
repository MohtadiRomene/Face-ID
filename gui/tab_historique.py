import tkinter as tk
from tkinter import ttk, messagebox
import os
from PIL import Image, ImageTk
from watermark.log_manager import verifier_log

LOGS_DIR = "logs"

class TabHistorique(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._construire_ui()
        self.rafraichir_logs()

    def _construire_ui(self):
        tk.Label(self, text="Historique des accès",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 4))

        # ── Tableau logs ──────────────────────────────────────────
        colonnes = ("fichier", "date", "statut")
        self.tree = ttk.Treeview(self, columns=colonnes,
                                  show="headings", height=10)
        self.tree.heading("fichier", text="Fichier")
        self.tree.heading("date",    text="Date")
        self.tree.heading("statut",  text="Statut")
        self.tree.column("fichier", width=260)
        self.tree.column("date",    width=160, anchor=tk.CENTER)
        self.tree.column("statut",  width=120, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self._afficher_image)

        # ── Miniature ─────────────────────────────────────────────
        frame_bas = tk.Frame(self)
        frame_bas.pack(fill=tk.X, padx=10, pady=5)

        self.label_img = tk.Label(frame_bas, bg="#2c3e50",
                                   width=160, height=120)
        self.label_img.pack(side=tk.LEFT, padx=8)

        frame_info = tk.Frame(frame_bas)
        frame_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.info_var = tk.StringVar(value="Sélectionnez un log.")
        tk.Label(frame_info, textvariable=self.info_var,
                 justify=tk.LEFT, wraplength=400,
                 font=("Helvetica", 9)).pack(anchor=tk.W, pady=4)

        # ── Boutons ───────────────────────────────────────────────
        frame_btn = tk.Frame(self)
        frame_btn.pack(fill=tk.X, padx=10, pady=4)

        tk.Button(frame_btn, text="Rafraîchir",
                  command=self.rafraichir_logs, width=12).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Vérifier watermark",
                  command=self._verifier_watermark,
                  bg="#2980b9", fg="white", width=18).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Supprimer ce log",
                  command=self._supprimer_log,
                  bg="#e74c3c", fg="white", width=16).pack(side=tk.RIGHT, padx=4)

    def rafraichir_logs(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not os.path.exists(LOGS_DIR):
            return
        for fichier in sorted(os.listdir(LOGS_DIR), reverse=True):
            if fichier.endswith(".png") and not fichier.startswith("_"):
                parties = fichier.replace(".png","").split("_")
                date    = parties[1] if len(parties) > 1 else "—"
                statut  = parties[3] if len(parties) > 3 else "—"
                self.tree.insert("", tk.END,
                                  values=(fichier, date, statut))

    def _afficher_image(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        nom_fichier = self.tree.item(sel[0])["values"][0]
        chemin      = os.path.join(LOGS_DIR, nom_fichier)
        if os.path.exists(chemin):
            img = Image.open(chemin).resize((160, 120))
            self._photo = ImageTk.PhotoImage(img)
            self.label_img.config(image=self._photo)

    def _verifier_watermark(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez un log.")
            return
        nom_fichier = self.tree.item(sel[0])["values"][0]
        chemin      = os.path.join(LOGS_DIR, nom_fichier)
        infos       = verifier_log(chemin)
        if infos:
            texte = "\n".join(f"{k} : {v}" for k, v in infos.items())
            self.info_var.set(f"Watermark vérifié :\n{texte}")
            self.app.set_statut("Watermark extrait avec succès.")
        else:
            self.info_var.set("Aucun watermark LSB trouvé dans ce fichier.")
            self.app.set_statut("Pas de watermark détecté.")

    def _supprimer_log(self):
        sel = self.tree.selection()
        if not sel:
            return
        nom_fichier = self.tree.item(sel[0])["values"][0]
        chemin      = os.path.join(LOGS_DIR, nom_fichier)
        if messagebox.askyesno("Confirmer", f"Supprimer {nom_fichier} ?"):
            os.remove(chemin)
            self.rafraichir_logs()
            self.app.set_statut(f"{nom_fichier} supprimé.")