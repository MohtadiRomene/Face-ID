from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QLineEdit, QComboBox, QCheckBox, QFileDialog,
                             QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class UsersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.rafraichir()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(24)

        # ── En-tête ───────────────────────────────────────────────
        header = QHBoxLayout()
        left_h = QVBoxLayout()
        left_h.setSpacing(4)
        title = QLabel("Gestion des utilisateurs")
        title.setObjectName("section_title")
        sub = QLabel("Ajoutez, modifiez ou retirez des accès au système.")
        sub.setObjectName("section_sub")
        left_h.addWidget(title)
        left_h.addWidget(sub)
        header.addLayout(left_h)
        header.addStretch()

        btn_train = QPushButton("  Entraîner le modèle IA")
        btn_train.setObjectName("btn_primary")
        btn_train.setFixedHeight(40)
        btn_train.clicked.connect(self._entrainer)
        header.addWidget(btn_train)
        root.addLayout(header)

        # ── Formulaire ajout ──────────────────────────────────────
        form_card = QFrame()
        form_card.setObjectName("card")
        form_lay = QVBoxLayout(form_card)
        form_lay.setContentsMargins(24, 20, 24, 20)
        form_lay.setSpacing(16)

        form_label = QLabel("NOUVEL UTILISATEUR")
        form_label.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                  "background:transparent;font-weight:500;")
        form_lay.addWidget(form_label)

        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)

        self._inp_nom    = self._make_input("Nom de famille")
        self._inp_prenom = self._make_input("Prénom")
        self._inp_role   = QComboBox()
        self._inp_role.addItems(["admin", "employé", "visiteur"])
        self._inp_role.setFixedHeight(42)
        self._inp_photo  = self._make_input("Chemin de la photo…")
        self._inp_photo.setReadOnly(True)

        btn_browse = QPushButton("Parcourir")
        btn_browse.setObjectName("btn_ghost")
        btn_browse.setFixedHeight(42)
        btn_browse.clicked.connect(self._choisir_photo)

        self._chk_autorise = QCheckBox("Autorisé")
        self._chk_autorise.setChecked(True)

        btn_add = QPushButton("Ajouter")
        btn_add.setObjectName("btn_success")
        btn_add.setFixedHeight(42)
        btn_add.clicked.connect(self._ajouter)

        fields_row.addWidget(self._inp_nom, 2)
        fields_row.addWidget(self._inp_prenom, 2)
        fields_row.addWidget(self._inp_role, 1)
        fields_row.addWidget(self._inp_photo, 3)
        fields_row.addWidget(btn_browse)
        fields_row.addWidget(self._chk_autorise)
        fields_row.addWidget(btn_add)
        form_lay.addLayout(fields_row)
        root.addWidget(form_card)

        # ── Tableau ───────────────────────────────────────────────
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["ID", "NOM", "PRÉNOM", "RÔLE", "AUTORISÉ", "PHOTO"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.setAlternatingRowColors(False)
        root.addWidget(self._table, 1)

        # ── Boutons table ─────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setObjectName("btn_ghost")
        btn_refresh.setFixedHeight(38)
        btn_refresh.clicked.connect(self.rafraichir)

        self._btn_toggle = QPushButton("Basculer autorisation")
        self._btn_toggle.setObjectName("btn_ghost")
        self._btn_toggle.setFixedHeight(38)
        self._btn_toggle.clicked.connect(self._toggle_autorise)

        btn_del = QPushButton("Supprimer la sélection")
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedHeight(38)
        btn_del.clicked.connect(self._supprimer)

        btn_row.addWidget(btn_refresh)
        btn_row.addWidget(self._btn_toggle)
        btn_row.addStretch()
        btn_row.addWidget(btn_del)
        root.addLayout(btn_row)

    def _make_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(42)
        return inp

    def rafraichir(self):
        try:
            from database.db_manager import get_tous_utilisateurs
            users = get_tous_utilisateurs()
        except Exception:
            users = []
        self._table.setRowCount(0)
        for u in users:
            row = self._table.rowCount()
            self._table.insertRow(row)
            items = [
                str(u.get("id", "")),
                u.get("nom", ""),
                u.get("prenom", ""),
                u.get("role", ""),
                "Oui" if u.get("autorise") else "Non",
                u.get("photo_path", "") or "—",
            ]
            for col, val in enumerate(items):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                if col == 4:
                    color = "#34D399" if val == "Oui" else "#F87171"
                    item.setForeground(QColor(color))
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self._table.setItem(row, col, item)
            self._table.setRowHeight(row, 48)

    def _choisir_photo(self):
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo", "", "Images (*.jpg *.jpeg *.png)")
        if chemin:
            self._inp_photo.setText(chemin)

    def _ajouter(self):
        nom    = self._inp_nom.text().strip()
        prenom = self._inp_prenom.text().strip()
        role   = self._inp_role.currentText()
        photo  = self._inp_photo.text().strip()
        autorise = 1 if self._chk_autorise.isChecked() else 0

        if not nom or not prenom:
            QMessageBox.warning(self, "Champs requis", "Nom et Prénom sont obligatoires.")
            return
        try:
            from database.db_manager import ajouter_utilisateur
            ajouter_utilisateur(nom, prenom,
                                photo_path=photo or None,
                                role=role,
                                autorise=autorise)
            self._inp_nom.clear()
            self._inp_prenom.clear()
            self._inp_photo.clear()
            self.rafraichir()
            QMessageBox.information(self, "Succès",
                                     f"Utilisateur {prenom} {nom} ajouté.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _toggle_autorise(self):
        sel = self._table.selectedItems()
        if not sel:
            QMessageBox.information(self, "Sélection", "Sélectionnez un utilisateur.")
            return
        row   = self._table.currentRow()
        uid   = int(self._table.item(row, 0).text())
        actuel = self._table.item(row, 4).text()
        nouvel = 0 if actuel == "Oui" else 1
        try:
            from database.db_manager import modifier_autorisation
            modifier_autorisation(uid, nouvel)
            self.rafraichir()
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _supprimer(self):
        sel = self._table.selectedItems()
        if not sel:
            QMessageBox.information(self, "Sélection", "Sélectionnez un utilisateur.")
            return
        row = self._table.currentRow()
        uid = int(self._table.item(row, 0).text())
        nom = f"{self._table.item(row, 1).text()} {self._table.item(row, 2).text()}"
        reply = QMessageBox.question(
            self, "Confirmer", f"Supprimer {nom} (#{uid}) ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                from database.db_manager import supprimer_utilisateur
                supprimer_utilisateur(uid)
                self.rafraichir()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", str(e))

    def _entrainer(self):
        reply = QMessageBox.question(
            self, "Entraîner le modèle",
            "Lancer l'entraînement du modèle LBPH avec toutes les photos ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        try:
            from recognition.trainer import entrainer_modele
            ok = entrainer_modele()
            if ok:
                QMessageBox.information(self, "Succès", "Modèle entraîné avec succès !")
            else:
                QMessageBox.warning(self, "Attention",
                                     "Entraînement échoué — ajoutez plus de photos (minimum 2).")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
