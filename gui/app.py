import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QLabel, QPushButton, QFrame,
                             QStackedWidget, QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon

from gui.styles          import DARK_THEME
from gui.page_login      import LoginPage
from gui.page_users      import UsersPage
from gui.page_historique import HistoriquePage


class NavButton(QPushButton):
    def __init__(self, icon_char, label, parent=None):
        super().__init__(f"  {icon_char}   {label}", parent)
        self.setObjectName("nav_btn")
        self.setFixedHeight(42)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(False)

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BiometriX — Système de contrôle d'accès")
        self.setMinimumSize(1200, 780)
        self.resize(1360, 860)

        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Sidebar ───────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)
        sb_lay.setAlignment(Qt.AlignTop)

        # Logo
        logo = QLabel("BIOMETRIX")
        logo.setObjectName("sidebar_logo")
        logo.setStyleSheet("color:#5B8DEF;font-size:16px;font-weight:700;"
                           "letter-spacing:3px;background:transparent;"
                           "padding:28px 20px 4px 20px;")
        sub_logo = QLabel("CONTRÔLE D'ACCÈS v2.0")
        sub_logo.setObjectName("sidebar_sub")
        sub_logo.setStyleSheet("color:#2D3748;font-size:9px;letter-spacing:2px;"
                                "background:transparent;padding:0 20px 20px 20px;")
        sb_lay.addWidget(logo)
        sb_lay.addWidget(sub_logo)

        # Séparateur
        div = QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        sb_lay.addWidget(div)

        # Nav principale
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("color:#2D3748;font-size:9px;letter-spacing:2px;"
                                 "background:transparent;padding:16px 20px 6px 20px;")
        sb_lay.addWidget(nav_label)

        self._nav_btns = []
        nav_items = [
            ("⬤", "Reconnaissance",  0),
            ("◈", "Utilisateurs",    1),
            ("▦", "Historique",      2),
        ]
        for icon, label, idx in nav_items:
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda checked, i=idx: self._switch_page(i))
            sb_lay.addWidget(btn)
            self._nav_btns.append(btn)

        div2 = QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QFrame.HLine)
        div2.setFixedHeight(1)
        div2.setStyleSheet("margin: 12px 0;")
        sb_lay.addWidget(div2)

        # Section système
        sys_label = QLabel("SYSTÈME")
        sys_label.setStyleSheet("color:#2D3748;font-size:9px;letter-spacing:2px;"
                                 "background:transparent;padding:4px 20px 6px 20px;")
        sb_lay.addWidget(sys_label)

        btn_quit = NavButton("⏻", "Quitter")
        btn_quit.clicked.connect(self.close)
        sb_lay.addWidget(btn_quit)

        sb_lay.addStretch()

        # Version / info bas
        ver = QLabel("v2.0  ·  LSB + LBPH + SQLite")
        ver.setStyleSheet("color:#1E2433;font-size:10px;background:transparent;"
                          "padding:16px 20px;")
        sb_lay.addWidget(ver)

        main_lay.addWidget(sidebar)

        # ── Stack de pages ────────────────────────────────────────
        right_side = QVBoxLayout()
        right_side.setContentsMargins(0, 0, 0, 0)
        right_side.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setObjectName("content_stack")

        self._page_login = LoginPage()
        self._page_users = UsersPage()
        self._page_histo  = HistoriquePage()

        self._stack.addWidget(self._page_login)
        self._stack.addWidget(self._page_users)
        self._stack.addWidget(self._page_histo)

        right_side.addWidget(self._stack)
        main_lay.addLayout(right_side, 1)

        # Page par défaut
        self._switch_page(0)

    def _switch_page(self, index: int):
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == index)
        # Rafraîchir l'historique à chaque visite
        if index == 2:
            self._page_histo.rafraichir()
        if index == 1:
            self._page_users.rafraichir()

    def closeEvent(self, event):
        self._page_login._arreter()
        super().closeEvent(event)


def lancer_app():
    from database.db_manager import init_db
    init_db()

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME)

    # Police système propre
    font = QFont("Segoe UI", 10)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
