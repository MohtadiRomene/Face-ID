import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database.db_manager import (get_tous_utilisateurs, ajouter_utilisateur,
                                  supprimer_utilisateur, get_utilisateur_par_id)
from recognition.trainer import entrainer_modele

class TabDashboard(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._construire_ui()
        self.rafraichir_liste()

    def _construire_ui(self):
        # ── Titre ────────────────────────────────────────────────
        tk.Label(self, text="Gestion des utilisateurs",
                 font=("Helvetica", 12, "bold")).pack(pady=(10, 4))

        # ── Tableau Treeview ──────────────────────────────────────
        colonnes = ("id", "nom", "prenom", "role", "autorise")
        self.tree = ttk.Treeview(self, columns=colonnes,
                                  show="headings", height=12)
        for col, larg in zip(colonnes, (50, 150, 150, 100, 80)):
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=larg, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # ── Formulaire ajout ──────────────────────────────────────
        frame_form = tk.LabelFrame(self, text="Ajouter un utilisateur",
                                    padx=8, pady=8)
        frame_form.pack(fill=tk.X, padx=10, pady=5)

        labels = ["Nom", "Prénom", "Rôle", "Photo"]
        self.champs = {}
        for i, lab in enumerate(labels):
            tk.Label(frame_form, text=lab+":").grid(row=0, column=i*2,
                                                     sticky=tk.W, padx=4)
            if lab == "Rôle":
                var = ttk.Combobox(frame_form, values=["admin","employe","visiteur"],
                                   width=10)
                var.set("employe")
            elif lab == "Photo":
                var = tk.Entry(frame_form, width=20)
            else:
                var = tk.Entry(frame_form, width=14)
            var.grid(row=0, column=i*2+1, padx=4)
            self.champs[lab] = var

        tk.Button(frame_form, text="Parcourir…",
                  command=self._choisir_photo).grid(row=0, column=8, padx=4)

        tk.Label(frame_form, text="Autorisé:").grid(row=0, column=9, padx=4)
        self.autorise_var = tk.IntVar(value=1)
        tk.Checkbutton(frame_form, variable=self.autorise_var).grid(row=0, column=10)

        # ── Boutons action ────────────────────────────────────────
        frame_btn = tk.Frame(self)
        frame_btn.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(frame_btn, text="Ajouter",
                  command=self._ajouter, bg="#27ae60", fg="white",
                  width=12).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Supprimer",
                  command=self._supprimer, bg="#e74c3c", fg="white",
                  width=12).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Rafraîchir",
                  command=self.rafraichir_liste,
                  width=12).pack(side=tk.LEFT, padx=4)
        tk.Button(frame_btn, text="Entraîner le modèle",
                  command=self._entrainer, bg="#2980b9", fg="white",
                  width=18).pack(side=tk.RIGHT, padx=4)

    def _choisir_photo(self):
        chemin = filedialog.askopenfilename(
            title="Choisir une photo",
            filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if chemin:
            self.champs["Photo"].delete(0, tk.END)
            self.champs["Photo"].insert(0, chemin)

    def rafraichir_liste(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for u in get_tous_utilisateurs():
            self.tree.insert("", tk.END, values=(
                u["id"], u["nom"], u["prenom"],
                u["role"], "Oui" if u["autorise"] else "Non"
            ))

    def _ajouter(self):
        nom    = self.champs["Nom"].get().strip()
        prenom = self.champs["Prénom"].get().strip()
        role   = self.champs["Rôle"].get().strip()
        photo  = self.champs["Photo"].get().strip()

        if not nom or not prenom:
            messagebox.showwarning("Champs manquants", "Nom et Prénom sont requis.")
            return

        ajouter_utilisateur(nom, prenom,
                            photo_path=photo or None,
                            role=role,
                            autorise=self.autorise_var.get())
        self.app.set_statut(f"Utilisateur {prenom} {nom} ajouté.")
        self.rafraichir_liste()

    def _supprimer(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sélection", "Sélectionnez un utilisateur.")
            return
        user_id = self.tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirmation",
                                f"Supprimer l'utilisateur #{user_id} ?"):
            supprimer_utilisateur(user_id)
            self.app.set_statut(f"Utilisateur #{user_id} supprimé.")
            self.rafraichir_liste()

    def _entrainer(self):
        self.app.set_statut("Entraînement en cours…")
        self.update()
        ok = entrainer_modele()
        if ok:
            self.app.set_statut("Modèle LBPH entraîné avec succès.")
            messagebox.showinfo("Entraînement", "Modèle entraîné avec succès !")
        else:
            self.app.set_statut("Entraînement échoué — pas assez d'images.")
            messagebox.showerror("Erreur", "Pas assez d'images (minimum 2).")