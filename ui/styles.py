"""QSS stylesheet definitions for the application."""


def get_stylesheet(dark_mode: bool = True) -> str:
    """Get the application stylesheet."""
    if dark_mode:
        return DARK_STYLE
    return LIGHT_STYLE


DARK_STYLE = """
QMainWindow {
    background-color: #1e1e1e;
}

QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#videoItem {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
    padding: 10px;
    margin: 4px;
}

QFrame#videoItem:hover {
    border: 1px solid #4d4d4d;
    background-color: #333333;
}

QLabel {
    color: #e0e0e0;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 14px;
    font-weight: bold;
    color: #ffffff;
}

QLabel#channelLabel {
    font-size: 12px;
    color: #aaaaaa;
}

QLabel#statusLabel {
    font-size: 11px;
    color: #888888;
}

QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 8px 12px;
    color: #e0e0e0;
    selection-background-color: #0078d4;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QLineEdit:disabled {
    background-color: #252525;
    color: #666666;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1084d8;
}

QPushButton:pressed {
    background-color: #006cbd;
}

QPushButton:disabled {
    background-color: #3d3d3d;
    color: #666666;
}

QPushButton#secondaryButton {
    background-color: #3d3d3d;
    color: #e0e0e0;
}

QPushButton#secondaryButton:hover {
    background-color: #4d4d4d;
}

QPushButton#dangerButton {
    background-color: #d41a1a;
}

QPushButton#dangerButton:hover {
    background-color: #e02020;
}

QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 6px 12px;
    color: #e0e0e0;
    min-width: 150px;
}

QComboBox:hover {
    border: 1px solid #4d4d4d;
}

QComboBox:focus {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #aaaaaa;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    selection-background-color: #0078d4;
    color: #e0e0e0;
}

QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #3d3d3d;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border: 1px solid #0078d4;
}

QCheckBox::indicator:hover {
    border: 1px solid #4d4d4d;
}

QProgressBar {
    background-color: #2d2d2d;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 4px;
}

QScrollArea {
    border: none;
    background-color: #1e1e1e;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3d3d3d;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4d4d4d;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QStatusBar {
    background-color: #252525;
    color: #aaaaaa;
    border-top: 1px solid #3d3d3d;
}

QMenuBar {
    background-color: #252525;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #3d3d3d;
}

QMenu {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    color: #e0e0e0;
}

QMenu::item:selected {
    background-color: #0078d4;
}

QDialog {
    background-color: #1e1e1e;
}

QGroupBox {
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #aaaaaa;
}

QSpinBox {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
}

QSpinBox:focus {
    border: 1px solid #0078d4;
}
"""


LIGHT_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QFrame#videoItem {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 10px;
    margin: 4px;
}

QFrame#videoItem:hover {
    border: 1px solid #c0c0c0;
    background-color: #fafafa;
}

QLabel {
    color: #333333;
    background-color: transparent;
}

QLabel#titleLabel {
    font-size: 14px;
    font-weight: bold;
    color: #1a1a1a;
}

QLabel#channelLabel {
    font-size: 12px;
    color: #666666;
}

QLabel#statusLabel {
    font-size: 11px;
    color: #888888;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 8px 12px;
    color: #333333;
    selection-background-color: #0078d4;
}

QLineEdit:focus {
    border: 1px solid #0078d4;
}

QLineEdit:disabled {
    background-color: #f0f0f0;
    color: #999999;
}

QPushButton {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #1084d8;
}

QPushButton:pressed {
    background-color: #006cbd;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
}

QPushButton#secondaryButton {
    background-color: #e0e0e0;
    color: #333333;
}

QPushButton#secondaryButton:hover {
    background-color: #d0d0d0;
}

QPushButton#dangerButton {
    background-color: #d41a1a;
}

QPushButton#dangerButton:hover {
    background-color: #e02020;
}

QComboBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 6px 12px;
    color: #333333;
    min-width: 150px;
}

QComboBox:hover {
    border: 1px solid #b0b0b0;
}

QComboBox:focus {
    border: 1px solid #0078d4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #666666;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    selection-background-color: #0078d4;
    selection-color: white;
    color: #333333;
}

QCheckBox {
    color: #333333;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #c0c0c0;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #0078d4;
    border: 1px solid #0078d4;
}

QCheckBox::indicator:hover {
    border: 1px solid #a0a0a0;
}

QProgressBar {
    background-color: #e0e0e0;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #0078d4;
    border-radius: 4px;
}

QScrollArea {
    border: none;
    background-color: #f5f5f5;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QStatusBar {
    background-color: #e8e8e8;
    color: #666666;
    border-top: 1px solid #d0d0d0;
}

QMenuBar {
    background-color: #e8e8e8;
    color: #333333;
}

QMenuBar::item:selected {
    background-color: #d0d0d0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    color: #333333;
}

QMenu::item:selected {
    background-color: #0078d4;
    color: white;
}

QDialog {
    background-color: #f5f5f5;
}

QGroupBox {
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #666666;
}

QSpinBox {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    padding: 4px 8px;
    color: #333333;
}

QSpinBox:focus {
    border: 1px solid #0078d4;
}
"""
