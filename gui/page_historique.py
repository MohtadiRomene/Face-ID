import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QTableWidget, QTableWidgetItem,
                             QSplitter, QMessageBox, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QColor

LOGS_DIR = "logs"


class HistoriquePage(QWidget):
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
        title = QLabel("Historique des accès")
        title.setObjectName("section_title")
        sub = QLabel("Consultez et vérifiez l'intégrité des logs tatouées numériquement.")
        sub.setObjectName("section_sub")
        left_h.addWidget(title)
        left_h.addWidget(sub)
        header.addLayout(left_h)
        header.addStretch()

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setObjectName("btn_ghost")
        btn_refresh.setFixedHeight(40)
        btn_refresh.clicked.connect(self.rafraichir)
        header.addWidget(btn_refresh)
        root.addLayout(header)

        # ── Splitter principal ────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("divider")

        # ── Tableau des logs ──────────────────────────────────────
        left_widget = QWidget()
        left_lay = QVBoxLayout(left_widget)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(12)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["FICHIER", "DATE", "HEURE", "STATUT"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setShowGrid(False)
        self._table.itemSelectionChanged.connect(self._on_select)
        left_lay.addWidget(self._table)

        btn_row = QHBoxLayout()
        btn_verify = QPushButton("Vérifier le watermark LSB")
        btn_verify.setObjectName("btn_primary")
        btn_verify.setFixedHeight(40)
        btn_verify.clicked.connect(self._verifier)

        btn_del = QPushButton("Supprimer")
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedHeight(40)
        btn_del.clicked.connect(self._supprimer)

        btn_row.addWidget(btn_verify)
        btn_row.addStretch()
        btn_row.addWidget(btn_del)
        left_lay.addLayout(btn_row)

        # ── Panneau détail droite ─────────────────────────────────
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_lay = QVBoxLayout(right_widget)
        right_lay.setContentsMargins(16, 0, 0, 0)
        right_lay.setSpacing(16)

        preview_label = QLabel("APERÇU")
        preview_label.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                     "background:transparent;")
        right_lay.addWidget(preview_label)

        self._preview = QLabel()
        self._preview.setAlignment(Qt.AlignCenter)
        self._preview.setMinimumHeight(200)
        self._preview.setStyleSheet("background:#080B10;border-radius:10px;"
                                     "color:#2D3748;font-size:13px;")
        self._preview.setText("Sélectionnez un log")
        right_lay.addWidget(self._preview)

        wm_label = QLabel("DONNÉES DU WATERMARK")
        wm_label.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                "background:transparent;margin-top:8px;")
        right_lay.addWidget(wm_label)

        self._wm_card = QFrame()
        self._wm_card.setObjectName("card")
        self._wm_lay = QVBoxLayout(self._wm_card)
        self._wm_lay.setContentsMargins(20, 16, 20, 16)
        self._wm_lay.setSpacing(10)
        self._wm_placeholder = QLabel("Cliquez sur «Vérifier le watermark LSB»\npour extraire les métadonnées cachées.")
        self._wm_placeholder.setStyleSheet("color:#4A5568;font-size:12px;background:transparent;")
        self._wm_placeholder.setWordWrap(True)
        self._wm_placeholder.setAlignment(Qt.AlignCenter)
        self._wm_lay.addWidget(self._wm_placeholder)
        right_lay.addWidget(self._wm_card)

        # Stats globales
        stats_label = QLabel("STATISTIQUES GLOBALES")
        stats_label.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                   "background:transparent;margin-top:8px;")
        right_lay.addWidget(stats_label)

        self._stats_card = QFrame()
        self._stats_card.setObjectName("card")
        s_lay = QVBoxLayout(self._stats_card)
        s_lay.setContentsMargins(20, 16, 20, 16)
        s_lay.setSpacing(8)
        self._stat_labels = {}
        for key, label in [("total", "Total de logs"),
                            ("autorise", "Accès autorisés"),
                            ("refuse", "Accès refusés"),
                            ("imposteur", "Imposteurs")]:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color:#6B7280;font-size:12px;background:transparent;")
            val = QLabel("0")
            val.setStyleSheet("color:#E8E6E1;font-size:13px;font-weight:500;"
                               "background:transparent;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            s_lay.addLayout(row)
            self._stat_labels[key] = val
        right_lay.addWidget(self._stats_card)
        right_lay.addStretch()

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter, 1)

    def rafraichir(self):
        self._table.setRowCount(0)
        counts = {"total": 0, "autorise": 0, "refuse": 0, "imposteur": 0}

        if not os.path.exists(LOGS_DIR):
            return

        fichiers = sorted(
            [f for f in os.listdir(LOGS_DIR)
             if f.endswith(".png") and not f.startswith("_")],
            reverse=True)

        for f in fichiers:
            parties = f.replace(".png", "").split("_")
            date    = parties[1] if len(parties) > 1 else "—"
            heure   = parties[2] if len(parties) > 2 else "—"
            statut  = parties[3] if len(parties) > 3 else "—"

            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(f))
            self._table.setItem(row, 1, QTableWidgetItem(date))
            self._table.setItem(row, 2, QTableWidgetItem(heure))

            stat_item = QTableWidgetItem(statut.upper())
            stat_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            colors = {"autorise": "#34D399", "refuse": "#FBBF24", "imposteur": "#F87171"}
            stat_item.setForeground(QColor(colors.get(statut, "#6B7280")))
            self._table.setItem(row, 3, stat_item)
            self._table.setRowHeight(row, 48)

            counts["total"] += 1
            if statut in counts:
                counts[statut] += 1

        for key, val in counts.items():
            if key in self._stat_labels:
                self._stat_labels[key].setText(str(val))

    def _on_select(self):
        sel = self._table.selectedItems()
        if not sel:
            return
        nom_fichier = self._table.item(self._table.currentRow(), 0).text()
        chemin = os.path.join(LOGS_DIR, nom_fichier)
        if os.path.exists(chemin):
            pix = QPixmap(chemin).scaled(
                280, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._preview.setPixmap(pix)
        # Reset watermark panel
        for i in reversed(range(self._wm_lay.count())):
            w = self._wm_lay.itemAt(i).widget()
            if w:
                w.deleteLater()
        self._wm_placeholder = QLabel("Cliquez sur «Vérifier le watermark LSB»\npour extraire les métadonnées.")
        self._wm_placeholder.setStyleSheet("color:#4A5568;font-size:12px;background:transparent;")
        self._wm_placeholder.setWordWrap(True)
        self._wm_placeholder.setAlignment(Qt.AlignCenter)
        self._wm_lay.addWidget(self._wm_placeholder)

    def _verifier(self):
        sel = self._table.selectedItems()
        if not sel:
            QMessageBox.information(self, "Sélection", "Sélectionnez un log.")
            return
        nom_fichier = self._table.item(self._table.currentRow(), 0).text()
        chemin = os.path.join(LOGS_DIR, nom_fichier)

        try:
            from watermark.log_manager import verifier_log
            infos = verifier_log(chemin)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))
            return

        # Vider panneau watermark
        for i in reversed(range(self._wm_lay.count())):
            w = self._wm_lay.itemAt(i).widget()
            if w:
                w.deleteLater()

        if infos:
            # Bandeau succès
            ok_banner = QLabel("✔  Watermark LSB vérifié avec succès")
            ok_banner.setStyleSheet("color:#34D399;font-size:12px;font-weight:500;"
                                     "background:#0A2A18;border-radius:6px;"
                                     "padding:8px 12px;")
            self._wm_lay.addWidget(ok_banner)

            friendly = {
                "user_id": "Identifiant utilisateur",
                "statut":  "Statut d'accès",
                "nom":     "Nom",
                "date":    "Horodatage",
            }
            for key, val in infos.items():
                row_lay = QHBoxLayout()
                lbl = QLabel(friendly.get(key, key))
                lbl.setStyleSheet("color:#6B7280;font-size:12px;background:transparent;")
                v = QLabel(str(val))
                color = "#34D399" if key == "statut" and val == "autorise" else \
                        "#F87171" if key == "statut" else "#E8E6E1"
                v.setStyleSheet(f"color:{color};font-size:12px;font-weight:500;"
                                 "background:transparent;")
                row_lay.addWidget(lbl)
                row_lay.addStretch()
                row_lay.addWidget(v)
                container = QWidget()
                container.setStyleSheet("background:transparent;")
                container.setLayout(row_lay)
                self._wm_lay.addWidget(container)
        else:
            err = QLabel("✘  Aucun watermark LSB détecté\n\nCe fichier n'a pas été créé\npar le système ou a été modifié.")
            err.setStyleSheet("color:#F87171;font-size:12px;background:#2A0A0A;"
                               "border-radius:6px;padding:10px 12px;")
            err.setWordWrap(True)
            err.setAlignment(Qt.AlignCenter)
            self._wm_lay.addWidget(err)

    def _supprimer(self):
        sel = self._table.selectedItems()
        if not sel:
            return
        nom_fichier = self._table.item(self._table.currentRow(), 0).text()
        chemin = os.path.join(LOGS_DIR, nom_fichier)
        reply = QMessageBox.question(
            self, "Confirmer", f"Supprimer définitivement {nom_fichier} ?",
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes and os.path.exists(chemin):
            os.remove(chemin)
            self.rafraichir()
            self._preview.clear()
            self._preview.setText("Sélectionnez un log")
