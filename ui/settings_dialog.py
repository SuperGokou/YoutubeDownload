"""Settings dialog for the application."""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QSpinBox, QCheckBox,
    QGroupBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal


class SettingsDialog(QDialog):
    """Settings/preferences dialog."""

    settings_changed = pyqtSignal(dict)

    def __init__(self, settings: dict, parent=None):
        super().__init__(parent)
        self.settings = settings.copy()
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Download settings group
        download_group = QGroupBox("Download Settings")
        download_layout = QFormLayout(download_group)

        # Output folder
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_btn)
        download_layout.addRow("Download Folder:", folder_layout)

        # Concurrent downloads
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 5)
        self.concurrent_spin.setValue(2)
        download_layout.addRow("Concurrent Downloads:", self.concurrent_spin)

        # Default quality
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Highest Available",
            "1080p",
            "720p",
            "480p",
            "360p",
            "Audio Only"
        ])
        download_layout.addRow("Default Quality:", self.quality_combo)

        layout.addWidget(download_group)

        # Subtitle settings group
        subtitle_group = QGroupBox("Subtitle Settings")
        subtitle_layout = QFormLayout(subtitle_group)

        # Auto download subtitles
        self.auto_subtitles = QCheckBox("Automatically download subtitles")
        subtitle_layout.addRow(self.auto_subtitles)

        # Preferred language
        self.subtitle_lang = QComboBox()
        self.subtitle_lang.addItems([
            "English (en)",
            "Spanish (es)",
            "French (fr)",
            "German (de)",
            "Portuguese (pt)",
            "Russian (ru)",
            "Japanese (ja)",
            "Korean (ko)",
            "Chinese (zh)",
        ])
        subtitle_layout.addRow("Preferred Language:", self.subtitle_lang)

        layout.addWidget(subtitle_group)

        # Appearance settings group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        self.dark_mode = QCheckBox("Dark Mode")
        self.dark_mode.setChecked(True)
        appearance_layout.addRow(self.dark_mode)

        layout.addWidget(appearance_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self._save_settings)

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    def _load_settings(self):
        """Load current settings into UI."""
        self.folder_input.setText(self.settings.get('download_folder', ''))
        self.concurrent_spin.setValue(self.settings.get('concurrent_downloads', 2))

        quality = self.settings.get('default_quality', 'Highest Available')
        idx = self.quality_combo.findText(quality)
        if idx >= 0:
            self.quality_combo.setCurrentIndex(idx)

        self.auto_subtitles.setChecked(self.settings.get('auto_subtitles', False))

        lang = self.settings.get('subtitle_language', 'en')
        for i in range(self.subtitle_lang.count()):
            if lang in self.subtitle_lang.itemText(i):
                self.subtitle_lang.setCurrentIndex(i)
                break

        self.dark_mode.setChecked(self.settings.get('dark_mode', True))

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            self.folder_input.text()
        )
        if folder:
            self.folder_input.setText(folder)

    def _save_settings(self):
        """Save settings and close dialog."""
        # Extract language code from combo text
        lang_text = self.subtitle_lang.currentText()
        lang_code = lang_text.split('(')[-1].rstrip(')') if '(' in lang_text else 'en'

        self.settings = {
            'download_folder': self.folder_input.text(),
            'concurrent_downloads': self.concurrent_spin.value(),
            'default_quality': self.quality_combo.currentText(),
            'auto_subtitles': self.auto_subtitles.isChecked(),
            'subtitle_language': lang_code,
            'dark_mode': self.dark_mode.isChecked(),
        }

        self.settings_changed.emit(self.settings)
        self.accept()

    def get_settings(self) -> dict:
        """Get the current settings."""
        return self.settings
