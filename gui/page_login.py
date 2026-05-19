from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np

class RecognitionThread(QThread):
    """Thread qui tourne la webcam + reconnaissance sans bloquer l'UI."""
    frame_ready    = pyqtSignal(np.ndarray, list)
    result_ready   = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running  = False
        self._detecteur = None
        self._modele    = None

    def _charger_modeles(self):
        try:
            from recognition.detector import charger_detecteur
            from recognition.trainer  import charger_modele
            self._detecteur = charger_detecteur()
            self._modele    = charger_modele()
            return True
        except FileNotFoundError as e:
            self.error_occurred.emit(str(e))
            return False

    def run(self):
        if not self._charger_modeles():
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error_occurred.emit("Impossible d'ouvrir la webcam.")
            return
        self._running = True
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break
            try:
                from recognition.recognizer import analyser_frame
                from watermark.log_manager import sauvegarder_log_tatatoue
                
                frame_annote, resultats = analyser_frame(
                    frame.copy(), self._detecteur, self._modele)
                self.frame_ready.emit(frame_annote, resultats)
                
                # Sauvegarder les logs pour chaque résultat
                for r in resultats:
                    sauvegarder_log_tatatoue(
                        frame,
                        user_id = r.get("user_id") or 0,
                        statut  = r.get("statut", "inconnu"),
                        nom     = r.get("nom", "Inconnu"),
                        confiance = r.get("confiance")
                    )
                    self.result_ready.emit(r)
            except Exception as e:
                print(f"[ERROR] {e}")
                self.frame_ready.emit(frame, [])
            self.msleep(30)
        cap.release()

    def stop(self):
        self._running = False
        self.wait()


class StatusBanner(QFrame):
    """Bandeau de statut animé en haut de la vue caméra."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("alert_success")
        self.setFixedHeight(56)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)

        self._dot = QLabel("●")
        self._dot.setStyleSheet("color:#34D399;font-size:10px;background:transparent;")
        self._msg = QLabel("En attente de reconnaissance…")
        self._msg.setStyleSheet("color:#34D399;font-size:14px;font-weight:500;background:transparent;")

        lay.addWidget(self._dot)
        lay.addWidget(self._msg)
        lay.addStretch()

    def set_state(self, statut: str, nom: str = ""):
        styles = {
            "attente":   ("alert_success", "#34D399", "●", "En attente de reconnaissance…"),
            "autorise":  ("alert_success", "#34D399", "✔", f"Accès autorisé — {nom}"),
            "refuse":    ("alert_warning", "#FBBF24", "⚠", f"Accès refusé — {nom}"),
            "imposteur": ("alert_danger",  "#F87171", "✘", "ALERTE — Imposteur détecté !"),
            "erreur":    ("alert_danger",  "#F87171", "⚠", nom),
        }
        frame_name, color, icon, msg = styles.get(statut, styles["attente"])
        self.setObjectName(frame_name)
        self._dot.setStyleSheet(f"color:{color};font-size:10px;background:transparent;")
        self._dot.setText(icon)
        self._msg.setStyleSheet(f"color:{color};font-size:14px;font-weight:500;background:transparent;")
        self._msg.setText(msg)
        self.style().unpolish(self)
        self.style().polish(self)


class LoginPage(QWidget):
    """
    Page principale : flux webcam + reconnaissance faciale.
    Signaux émis vers la fenêtre principale pour changer de vue.
    """
    acces_autorise = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._last_result = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ──────────────────────────────────────────────
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(56)
        tb_lay = QHBoxLayout(topbar)
        tb_lay.setContentsMargins(24, 0, 24, 0)

        logo = QLabel("BIOMETRIX")
        logo.setStyleSheet("color:#5B8DEF;font-size:15px;font-weight:700;"
                           "letter-spacing:3px;background:transparent;")
        self._status_badge = QLabel("SYSTÈME EN VEILLE")
        self._status_badge.setObjectName("status_badge")
        tb_lay.addWidget(logo)
        tb_lay.addStretch()
        tb_lay.addWidget(self._status_badge)
        root.addWidget(topbar)

        # ── Corps principal ───────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(40, 40, 40, 40)
        body.setSpacing(32)

        # ── Colonne gauche : caméra ───────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(16)

        cam_frame = QFrame()
        cam_frame.setObjectName("camera_frame")
        cam_lay = QVBoxLayout(cam_frame)
        cam_lay.setContentsMargins(0, 0, 0, 0)

        self._cam_label = QLabel()
        self._cam_label.setObjectName("camera_label")
        self._cam_label.setAlignment(Qt.AlignCenter)
        self._cam_label.setMinimumSize(580, 435)
        self._cam_label.setText("⬛  Caméra inactive\n\nAppuyez sur «Démarrer» pour lancer la reconnaissance")
        self._cam_label.setStyleSheet(
            "color:#2D3748;font-size:15px;background:#080B10;border-radius:10px;")
        cam_lay.addWidget(self._cam_label)

        self._status_banner = StatusBanner()
        cam_lay.addWidget(self._status_banner)
        left.addWidget(cam_frame)

        # Boutons caméra
        btn_row = QHBoxLayout()
        self._btn_start = QPushButton("  Démarrer la reconnaissance")
        self._btn_start.setObjectName("btn_primary")
        self._btn_start.setFixedHeight(44)
        self._btn_start.clicked.connect(self._demarrer)

        self._btn_stop = QPushButton("Arrêter")
        self._btn_stop.setObjectName("btn_ghost")
        self._btn_stop.setFixedHeight(44)
        self._btn_stop.setEnabled(False)
        self._btn_stop.clicked.connect(self._arreter)

        btn_row.addWidget(self._btn_start, 3)
        btn_row.addWidget(self._btn_stop, 1)
        left.addLayout(btn_row)

        # ── Colonne droite : info & logs récents ──────────────────
        right = QVBoxLayout()
        right.setSpacing(16)
        right.setAlignment(Qt.AlignTop)

        # Carte identité reconnue
        self._id_card = self._make_id_card()
        right.addWidget(self._id_card)

        # Statistiques rapides
        stats_title = QLabel("STATISTIQUES")
        stats_title.setObjectName("sidebar_sub")
        stats_title.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                   "background:transparent;padding:8px 0 4px 0;")
        right.addWidget(stats_title)

        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(10)
        self._stat_ok    = self._make_stat_card("AUTORISÉS", "0", "green")
        self._stat_refus = self._make_stat_card("REFUSÉS",   "0", "amber")
        self._stat_imp   = self._make_stat_card("IMPOSTEURS","0", "red")
        stats_grid.addWidget(self._stat_ok)
        stats_grid.addWidget(self._stat_refus)
        stats_grid.addWidget(self._stat_imp)
        right.addLayout(stats_grid)

        # Log en temps réel
        log_title = QLabel("ÉVÉNEMENTS RÉCENTS")
        log_title.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:2px;"
                                 "background:transparent;padding:8px 0 4px 0;")
        right.addWidget(log_title)

        self._log_frame = QFrame()
        self._log_frame.setObjectName("card")
        self._log_frame.setMinimumHeight(180)
        log_lay = QVBoxLayout(self._log_frame)
        log_lay.setSpacing(0)
        log_lay.setContentsMargins(0, 0, 0, 0)
        self._log_entries = []
        for _ in range(5):
            lbl = QLabel("—")
            lbl.setStyleSheet("color:#2D3748;font-size:12px;background:transparent;"
                              "padding:8px 16px;border-bottom:1px solid #1A1F2E;")
            log_lay.addWidget(lbl)
            self._log_entries.append(lbl)
        right.addWidget(self._log_frame)

        right.addStretch()

        body.addLayout(left, 3)
        body.addLayout(right, 1)
        root.addLayout(body, 1)

        # Compteurs
        self._cnt = {"autorise": 0, "refuse": 0, "imposteur": 0}
        self._recent_logs = []

    # ── Carte identité ─────────────────────────────────────────────
    def _make_id_card(self):
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(10)

        header = QHBoxLayout()
        self._avatar = QLabel("?")
        self._avatar.setFixedSize(52, 52)
        self._avatar.setAlignment(Qt.AlignCenter)
        self._avatar.setStyleSheet("background:#1A2035;color:#5B8DEF;"
                                    "border-radius:26px;font-size:20px;font-weight:600;")
        self._id_name = QLabel("En attente…")
        self._id_name.setObjectName("section_title")
        self._id_name.setStyleSheet("color:#E8E6E1;font-size:16px;font-weight:600;"
                                     "background:transparent;")
        self._id_role = QLabel("—")
        self._id_role.setStyleSheet("color:#6B7280;font-size:12px;background:transparent;")
        info = QVBoxLayout()
        info.setSpacing(2)
        info.addWidget(self._id_name)
        info.addWidget(self._id_role)
        header.addWidget(self._avatar)
        header.addSpacing(12)
        header.addLayout(info)
        header.addStretch()
        self._id_badge = QLabel("—")
        self._id_badge.setStyleSheet(
            "background:#1E2433;color:#6B7280;border-radius:12px;"
            "padding:4px 12px;font-size:11px;font-weight:500;")
        header.addWidget(self._id_badge)
        lay.addLayout(header)

        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        lay.addWidget(div)

        self._id_detail = QLabel("Aucune reconnaissance en cours.")
        self._id_detail.setStyleSheet("color:#4A5568;font-size:12px;background:transparent;")
        self._id_detail.setWordWrap(True)
        lay.addWidget(self._id_detail)
        return card

    def _make_stat_card(self, title, value, color):
        card = QFrame()
        name = {"green": "card_accent_green",
                "red":   "card_accent_red",
                "amber": "card_accent_amber"}.get(color, "card")
        card.setObjectName(name)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet("color:#4A5568;font-size:10px;letter-spacing:1px;background:transparent;")
        v = QLabel(value)
        vc = {"green": "#34D399", "red": "#F87171", "amber": "#FBBF24"}.get(color, "#E8E6E1")
        v.setStyleSheet(f"color:{vc};font-size:26px;font-weight:600;background:transparent;")
        lay.addWidget(t)
        lay.addWidget(v)
        card._value_label = v
        return card

    # ── Caméra ─────────────────────────────────────────────────────
    def _demarrer(self):
        self._thread = RecognitionThread()
        self._thread.frame_ready.connect(self._on_frame)
        self._thread.result_ready.connect(self._on_result)
        self._thread.error_occurred.connect(self._on_error)
        self._thread.start()
        self._btn_start.setEnabled(False)
        self._btn_stop.setEnabled(True)
        self._status_badge.setText("RECONNAISSANCE ACTIVE")
        self._status_badge.setProperty("status", "active")
        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)
        self._status_banner.set_state("attente")

    def _arreter(self):
        if self._thread:
            self._thread.stop()
        self._btn_start.setEnabled(True)
        self._btn_stop.setEnabled(False)
        self._cam_label.clear()
        self._cam_label.setText("⬛  Caméra inactive\n\nAppuyez sur «Démarrer» pour lancer la reconnaissance")
        self._status_badge.setText("SYSTÈME EN VEILLE")
        self._status_badge.setProperty("status", "")
        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)
        self._status_banner.set_state("attente")
        self._reset_id_card()

    def _on_frame(self, frame, resultats):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qt_img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(qt_img).scaled(
            self._cam_label.width(), self._cam_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._cam_label.setPixmap(pix)

    def _on_result(self, r):
        statut = r.get("statut", "attente")
        nom    = r.get("nom", "")
        uid    = r.get("user_id")

        self._status_banner.set_state(statut, nom)

        # Mise à jour carte identité
        if statut == "autorise":
            self._avatar.setText(nom[0].upper() if nom else "?")
            self._avatar.setStyleSheet("background:#0A2A18;color:#34D399;"
                                        "border-radius:26px;font-size:20px;font-weight:600;")
            self._id_name.setText(nom)
            self._id_role.setText(f"ID #{uid}" if uid else "—")
            self._id_badge.setText("AUTORISÉ")
            self._id_badge.setStyleSheet(
                "background:#0A2A18;color:#34D399;border-radius:12px;"
                "padding:4px 12px;font-size:11px;font-weight:600;")
            score = r.get("score_pct")
            if score is None:
                dist = r.get("confiance", 0)
                score = max(0.0, min(100.0, (1.0 - dist / 62.0) * 100.0))
            self._id_detail.setText(f"Correspondance : {score:.0f} %")
            self._cnt["autorise"] += 1
            self._stat_ok._value_label.setText(str(self._cnt["autorise"]))
            self._log_event("autorise", nom)

        elif statut == "refuse":
            self._avatar.setText("!")
            self._avatar.setStyleSheet("background:#2A1F0A;color:#FBBF24;"
                                        "border-radius:26px;font-size:20px;font-weight:600;")
            self._id_name.setText(nom)
            self._id_badge.setText("REFUSÉ")
            self._id_badge.setStyleSheet(
                "background:#2A1F0A;color:#FBBF24;border-radius:12px;"
                "padding:4px 12px;font-size:11px;font-weight:600;")
            self._cnt["refuse"] += 1
            self._stat_refus._value_label.setText(str(self._cnt["refuse"]))
            self._log_event("refuse", nom)

        elif statut == "imposteur":
            self._avatar.setText("✘")
            self._avatar.setStyleSheet("background:#2A0A0A;color:#F87171;"
                                        "border-radius:26px;font-size:20px;font-weight:600;")
            self._id_name.setText("IMPOSTEUR")
            self._id_badge.setText("ALARME")
            self._id_badge.setStyleSheet(
                "background:#2A0A0A;color:#F87171;border-radius:12px;"
                "padding:4px 12px;font-size:11px;font-weight:600;")
            self._cnt["imposteur"] += 1
            self._stat_imp._value_label.setText(str(self._cnt["imposteur"]))
            self._log_event("imposteur", "Inconnu")

    def _on_error(self, msg):
        self._status_banner.set_state("erreur", msg)
        self._arreter()

    def _log_event(self, statut, nom):
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        colors = {"autorise": "#34D399", "refuse": "#FBBF24", "imposteur": "#F87171"}
        icons  = {"autorise": "✔", "refuse": "⚠", "imposteur": "✘"}
        c = colors.get(statut, "#6B7280")
        i = icons.get(statut, "—")
        msg = f'<span style="color:{c}">{i}</span>  <span style="color:#C9C7C0">{nom}</span>  <span style="color:#4A5568">{now}</span>'
        self._recent_logs.insert(0, msg)
        self._recent_logs = self._recent_logs[:5]
        for idx, lbl in enumerate(self._log_entries):
            if idx < len(self._recent_logs):
                lbl.setText(self._recent_logs[idx])
                lbl.setStyleSheet("font-size:12px;background:transparent;"
                                   "padding:8px 16px;border-bottom:1px solid #1A1F2E;")
            else:
                lbl.setText("—")
                lbl.setStyleSheet("color:#2D3748;font-size:12px;background:transparent;"
                                   "padding:8px 16px;border-bottom:1px solid #1A1F2E;")

    def _reset_id_card(self):
        self._avatar.setText("?")
        self._avatar.setStyleSheet("background:#1A2035;color:#5B8DEF;"
                                    "border-radius:26px;font-size:20px;font-weight:600;")
        self._id_name.setText("En attente…")
        self._id_role.setText("—")
        self._id_badge.setText("—")
        self._id_badge.setStyleSheet(
            "background:#1E2433;color:#6B7280;border-radius:12px;"
            "padding:4px 12px;font-size:11px;font-weight:500;")
        self._id_detail.setText("Aucune reconnaissance en cours.")

    def closeEvent(self, event):
        self._arreter()
        super().closeEvent(event)
