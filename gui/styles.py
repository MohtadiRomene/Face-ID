DARK_THEME = """
/* ─── Global ─────────────────────────────────────────────────── */
QWidget {
    background-color: #0F1117;
    color: #E8E6E1;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0F1117;
}

/* ─── Sidebar ─────────────────────────────────────────────────── */
#sidebar {
    background-color: #080B10;
    border-right: 1px solid #1E2433;
    min-width: 220px;
    max-width: 220px;
}

#sidebar_logo {
    background-color: transparent;
    color: #E8E6E1;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 28px 20px 8px 20px;
}

#sidebar_sub {
    background-color: transparent;
    color: #4A5568;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 0px 20px 24px 20px;
}

QPushButton#nav_btn {
    background-color: transparent;
    color: #6B7280;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 400;
    margin: 2px 8px;
}
QPushButton#nav_btn:hover {
    background-color: #141824;
    color: #C9C7C0;
}
QPushButton#nav_btn[active="true"] {
    background-color: #1A2035;
    color: #5B8DEF;
    font-weight: 500;
}

#sidebar_section_label {
    background-color: transparent;
    color: #2D3748;
    font-size: 10px;
    letter-spacing: 2px;
    padding: 16px 20px 6px 20px;
}

/* ─── Main content area ────────────────────────────────────────── */
#content_stack {
    background-color: #0F1117;
}

/* ─── Top bar ─────────────────────────────────────────────────── */
#topbar {
    background-color: #080B10;
    border-bottom: 1px solid #1E2433;
    min-height: 56px;
    max-height: 56px;
    padding: 0 24px;
}

#topbar_title {
    background-color: transparent;
    color: #E8E6E1;
    font-size: 16px;
    font-weight: 600;
}

#status_badge {
    background-color: #0D2137;
    color: #5B8DEF;
    border: 1px solid #1E3A5F;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 11px;
    letter-spacing: 0.5px;
}

#status_badge[status="active"] {
    background-color: #0D2A1A;
    color: #34D399;
    border-color: #1A4A30;
}

#status_badge[status="alert"] {
    background-color: #2D1515;
    color: #F87171;
    border-color: #4A2020;
}

/* ─── Cards ────────────────────────────────────────────────────── */
QFrame#card {
    background-color: #141824;
    border: 1px solid #1E2433;
    border-radius: 12px;
    padding: 20px;
}

QFrame#card_accent_green {
    background-color: #0A1F14;
    border: 1px solid #1A3D28;
    border-radius: 12px;
    padding: 20px;
}

QFrame#card_accent_red {
    background-color: #1F0A0A;
    border: 1px solid #3D1A1A;
    border-radius: 12px;
    padding: 20px;
}

QFrame#card_accent_amber {
    background-color: #1F180A;
    border: 1px solid #3D2E1A;
    border-radius: 12px;
    padding: 20px;
}

#card_title {
    background-color: transparent;
    color: #6B7280;
    font-size: 11px;
    letter-spacing: 1.5px;
}

#card_value {
    background-color: transparent;
    color: #E8E6E1;
    font-size: 28px;
    font-weight: 600;
}

#card_value_green { color: #34D399; font-size: 28px; font-weight: 600; background: transparent; }
#card_value_red   { color: #F87171; font-size: 28px; font-weight: 600; background: transparent; }
#card_value_amber { color: #FBBF24; font-size: 28px; font-weight: 600; background: transparent; }

/* ─── Camera view ─────────────────────────────────────────────── */
#camera_frame {
    background-color: #080B10;
    border: 1px solid #1E2433;
    border-radius: 12px;
}

#camera_label {
    background-color: #080B10;
    border-radius: 10px;
    color: #2D3748;
    font-size: 14px;
}

/* ─── Buttons ─────────────────────────────────────────────────── */
QPushButton#btn_primary {
    background-color: #2355C3;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.3px;
}
QPushButton#btn_primary:hover { background-color: #2D65D8; }
QPushButton#btn_primary:pressed { background-color: #1A44A0; }
QPushButton#btn_primary:disabled { background-color: #1E2433; color: #4A5568; }

QPushButton#btn_danger {
    background-color: #7F1D1D;
    color: #FCA5A5;
    border: 1px solid #991B1B;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#btn_danger:hover { background-color: #991B1B; }
QPushButton#btn_danger:pressed { background-color: #6B1515; }

QPushButton#btn_ghost {
    background-color: transparent;
    color: #6B7280;
    border: 1px solid #1E2433;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
}
QPushButton#btn_ghost:hover {
    background-color: #141824;
    color: #C9C7C0;
    border-color: #2D3748;
}

QPushButton#btn_success {
    background-color: #064E2F;
    color: #34D399;
    border: 1px solid #065F46;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton#btn_success:hover { background-color: #065F46; }
QPushButton#btn_success:disabled { background-color: #1E2433; color: #4A5568; border-color: #1E2433; }

/* ─── Table / TreeView ─────────────────────────────────────────── */
QTableWidget, QTreeWidget {
    background-color: #0F1117;
    border: 1px solid #1E2433;
    border-radius: 8px;
    gridline-color: #1E2433;
    outline: none;
    selection-background-color: #1A2035;
    selection-color: #E8E6E1;
    font-size: 13px;
}

QTableWidget::item, QTreeWidget::item {
    padding: 10px 12px;
    border-bottom: 1px solid #1A1F2E;
    color: #C9C7C0;
}

QTableWidget::item:selected, QTreeWidget::item:selected {
    background-color: #1A2035;
    color: #E8E6E1;
}

QHeaderView::section {
    background-color: #080B10;
    color: #4A5568;
    border: none;
    border-bottom: 1px solid #1E2433;
    padding: 10px 12px;
    font-size: 11px;
    letter-spacing: 1px;
    font-weight: 500;
}

/* ─── Inputs ───────────────────────────────────────────────────── */
QLineEdit, QComboBox, QTextEdit {
    background-color: #141824;
    color: #E8E6E1;
    border: 1px solid #2D3748;
    border-radius: 8px;
    padding: 9px 14px;
    font-size: 13px;
    selection-background-color: #2355C3;
}
QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #5B8DEF;
    background-color: #141824;
}
QLineEdit::placeholder { color: #4A5568; }

QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: #141824;
    border: 1px solid #2D3748;
    border-radius: 8px;
    selection-background-color: #1A2035;
    color: #E8E6E1;
}

/* ─── Scrollbars ───────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #080B10;
    width: 6px;
    margin: 0;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #2D3748;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #4A5568; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { height: 6px; background: #080B10; border-radius: 3px; }
QScrollBar::handle:horizontal { background: #2D3748; border-radius: 3px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

/* ─── Checkboxes ───────────────────────────────────────────────── */
QCheckBox {
    color: #C9C7C0;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #2D3748;
    background-color: #141824;
}
QCheckBox::indicator:checked {
    background-color: #2355C3;
    border-color: #2355C3;
}

/* ─── Labels ───────────────────────────────────────────────────── */
QLabel#section_title {
    color: #E8E6E1;
    font-size: 18px;
    font-weight: 600;
    background: transparent;
}

QLabel#section_sub {
    color: #6B7280;
    font-size: 13px;
    background: transparent;
}

/* ─── Alert banner ─────────────────────────────────────────────── */
QFrame#alert_success {
    background-color: #0A2A18;
    border: 1px solid #1A4A30;
    border-radius: 10px;
    padding: 14px 18px;
}
QFrame#alert_danger {
    background-color: #2A0A0A;
    border: 1px solid #4A1A1A;
    border-radius: 10px;
    padding: 14px 18px;
}
QFrame#alert_warning {
    background-color: #2A1F0A;
    border: 1px solid #4A341A;
    border-radius: 10px;
    padding: 14px 18px;
}

/* ─── Divider ──────────────────────────────────────────────────── */
QFrame#divider {
    background-color: #1E2433;
    max-height: 1px;
    border: none;
}

/* ─── Splitter ─────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #1E2433;
    width: 1px;
}

/* ─── Progress bar ─────────────────────────────────────────────── */
QProgressBar {
    background-color: #141824;
    border: 1px solid #1E2433;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2355C3;
    border-radius: 4px;
}
"""
