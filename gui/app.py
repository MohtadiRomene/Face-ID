import tkinter as tk
from tkinter import ttk
from gui.tab_dashboard  import TabDashboard
from gui.tab_camera     import TabCamera
from gui.tab_historique import TabHistorique

class BiometrieApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Système Biométrique — Contrôle d'accès")
        self.geometry("900x650")
        self.resizable(True, True)

        # ── Barre de titre ───────────────────────────────────────
        titre = tk.Label(self, text="Système de Reconnaissance Faciale",
                         font=("Helvetica", 14, "bold"), pady=8)
        titre.pack(side=tk.TOP, fill=tk.X)

        # ── Notebook (onglets) ────────────────────────────────────
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tab1 = TabDashboard(self.notebook, self)
        self.tab2 = TabCamera(self.notebook, self)
        self.tab3 = TabHistorique(self.notebook, self)

        self.notebook.add(self.tab1, text="  Dashboard admin  ")
        self.notebook.add(self.tab2, text="  Caméra live  ")
        self.notebook.add(self.tab3, text="  Historique des accès  ")

        # ── Barre de statut ───────────────────────────────────────
        self.statut_var = tk.StringVar(value="Prêt.")
        barre = tk.Label(self, textvariable=self.statut_var,
                         anchor=tk.W, relief=tk.SUNKEN,
                         font=("Helvetica", 9), pady=4, padx=8)
        barre.pack(side=tk.BOTTOM, fill=tk.X)

        # Arrêt propre de la caméra à la fermeture
        self.protocol("WM_DELETE_WINDOW", self._quitter)

    def set_statut(self, message: str):
        self.statut_var.set(message)
        self.update_idletasks()

    def _quitter(self):
        self.tab2.arreter_camera()
        self.destroy()

def lancer_app():
    from database.db_manager import init_db
    init_db()
    app = BiometrieApp()
    app.mainloop()