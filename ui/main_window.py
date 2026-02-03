"""Main application window."""

import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QScrollArea, QFrame,
    QStatusBar, QLabel, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSettings

from .video_item_widget import VideoItemWidget
from .settings_dialog import SettingsDialog
from .styles import get_stylesheet
from core.video_info import VideoInfoFetcher, VideoInfo
from core.downloader import DownloadManager, DownloadStatus
from core.utils import get_download_folder, parse_urls, is_playlist_url


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()

        # Initialize settings
        self.settings = {
            'download_folder': get_download_folder(),
            'concurrent_downloads': 2,
            'default_quality': 'Highest Available',
            'auto_subtitles': False,
            'subtitle_language': 'en',
            'dark_mode': True,
        }
        self._load_settings()

        # Initialize managers
        self.video_fetcher = VideoInfoFetcher(self)
        self.download_manager = DownloadManager(
            max_concurrent=self.settings['concurrent_downloads'],
            parent=self
        )
        self.download_manager.set_output_path(self.settings['download_folder'])

        # Video item widgets mapping: task_id -> widget
        self.video_widgets: dict[str, VideoItemWidget] = {}

        # Set up UI
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()

    def _setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Top bar - URL input
        top_bar = QHBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL here (video or playlist)...")
        self.url_input.returnPressed.connect(self._on_add_url)
        top_bar.addWidget(self.url_input, 1)

        self.paste_btn = QPushButton("Paste")
        self.paste_btn.clicked.connect(self._on_paste)
        top_bar.addWidget(self.paste_btn)

        self.add_btn = QPushButton("Download")
        self.add_btn.clicked.connect(self._on_add_url)
        top_bar.addWidget(self.add_btn)

        top_bar.addSpacing(20)

        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("secondaryButton")
        self.settings_btn.clicked.connect(self._on_settings)
        top_bar.addWidget(self.settings_btn)

        main_layout.addLayout(top_bar)

        # Download list header
        header = QLabel("Download List")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px 0;")
        main_layout.addWidget(header)

        # Scrollable video list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.list_container = QWidget()
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setSpacing(8)
        self.list_layout.setContentsMargins(0, 0, 8, 0)
        self.list_layout.addStretch()

        self.scroll_area.setWidget(self.list_container)
        main_layout.addWidget(self.scroll_area, 1)

        # Empty state label
        self.empty_label = QLabel("No videos in queue. Paste a YouTube URL above to get started.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #888888; font-size: 14px; padding: 40px;")
        self.list_layout.insertWidget(0, self.empty_label)

        # Bottom action bar
        bottom_bar = QHBoxLayout()

        self.download_all_btn = QPushButton("Download All")
        self.download_all_btn.clicked.connect(self._on_download_all)
        self.download_all_btn.setEnabled(False)
        bottom_bar.addWidget(self.download_all_btn)

        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.setObjectName("secondaryButton")
        self.clear_btn.clicked.connect(self._on_clear_list)
        self.clear_btn.setEnabled(False)
        bottom_bar.addWidget(self.clear_btn)

        bottom_bar.addStretch()

        self.open_folder_btn = QPushButton("Open Download Folder")
        self.open_folder_btn.setObjectName("secondaryButton")
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        bottom_bar.addWidget(self.open_folder_btn)

        main_layout.addLayout(bottom_bar)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

    def _connect_signals(self):
        """Connect all signals."""
        # Video fetcher signals
        self.video_fetcher.video_info_ready.connect(self._on_video_info_ready)
        self.video_fetcher.playlist_video_found.connect(self._on_playlist_video_found)
        self.video_fetcher.error.connect(self._on_fetch_error)
        self.video_fetcher.progress.connect(self._on_fetch_progress)

        # Download manager signals
        self.download_manager.task_progress.connect(self._on_download_progress)
        self.download_manager.task_status.connect(self._on_download_status)
        self.download_manager.task_finished.connect(self._on_download_finished)
        self.download_manager.task_error.connect(self._on_download_error)
        self.download_manager.queue_status.connect(self._on_queue_status)

    def _apply_theme(self):
        """Apply the current theme stylesheet."""
        stylesheet = get_stylesheet(self.settings['dark_mode'])
        self.setStyleSheet(stylesheet)

    def _load_settings(self):
        """Load settings from file."""
        settings_path = os.path.join(os.path.expanduser("~"), ".youtube_downloader_settings.json")
        try:
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    saved = json.load(f)
                    self.settings.update(saved)
        except Exception:
            pass

    def _save_settings(self):
        """Save settings to file."""
        settings_path = os.path.join(os.path.expanduser("~"), ".youtube_downloader_settings.json")
        try:
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _update_empty_state(self):
        """Update visibility of empty state label."""
        has_videos = len(self.video_widgets) > 0
        self.empty_label.setVisible(not has_videos)
        self.download_all_btn.setEnabled(has_videos)
        self.clear_btn.setEnabled(has_videos)

    def _on_paste(self):
        """Paste from clipboard."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.url_input.setText(text)
            self._on_add_url()

    def _on_add_url(self):
        """Add URL(s) from input field."""
        text = self.url_input.text().strip()
        if not text:
            return

        # Parse URLs from input
        urls = parse_urls(text)
        if not urls:
            self.status_label.setText("No valid YouTube URLs found")
            return

        self.url_input.clear()
        self.url_input.setEnabled(False)
        self.add_btn.setEnabled(False)

        for url in urls:
            self.video_fetcher.fetch_url(url)

    def _on_video_info_ready(self, video_info: VideoInfo):
        """Handle video info fetched."""
        self.url_input.setEnabled(True)
        self.add_btn.setEnabled(True)

        # Add to download manager
        itag = video_info.streams[0].itag if video_info.streams else None
        if not itag and video_info.audio_streams:
            itag = video_info.audio_streams[0].itag

        if not itag:
            self.status_label.setText(f"No streams available for: {video_info.title}")
            return

        task_id = self.download_manager.add_task(
            video_info=video_info,
            itag=itag,
            audio_only=False,
            subtitles=self.settings['auto_subtitles'],
            subtitle_lang=self.settings['subtitle_language'],
        )

        # Create widget
        widget = VideoItemWidget(task_id, video_info)
        widget.download_clicked.connect(self._on_item_download)
        widget.remove_clicked.connect(self._on_item_remove)
        widget.settings_changed.connect(self._on_item_settings_changed)

        self.video_widgets[task_id] = widget

        # Add to layout (before the stretch)
        self.list_layout.insertWidget(self.list_layout.count() - 1, widget)
        self._update_empty_state()

        self.status_label.setText(f"Added: {video_info.title}")

    def _on_playlist_video_found(self, url: str):
        """Handle video found in playlist."""
        # Fetch info for each video in playlist
        self.video_fetcher.fetch_url(url)

    def _on_fetch_error(self, error: str):
        """Handle fetch error."""
        self.url_input.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error}")
        QMessageBox.warning(self, "Error", f"Failed to fetch video info:\n{error}")

    def _on_fetch_progress(self, message: str):
        """Handle fetch progress update."""
        self.status_label.setText(message)

    def _on_item_download(self, task_id: str):
        """Handle individual item download button."""
        task = self.download_manager.get_task(task_id)
        if task and task.status == DownloadStatus.DOWNLOADING:
            # Cancel
            self.download_manager.cancel_task(task_id)
        else:
            # Update task settings from widget
            widget = self.video_widgets.get(task_id)
            if widget:
                task.selected_itag = widget.get_selected_itag()
                task.audio_only = widget.is_audio_only()
                task.download_subtitles = widget.wants_subtitles()

            self.download_manager.start_task(task_id)

    def _on_item_remove(self, task_id: str):
        """Handle item remove button."""
        self.download_manager.remove_task(task_id)

        if task_id in self.video_widgets:
            widget = self.video_widgets.pop(task_id)
            widget.deleteLater()

        self._update_empty_state()

    def _on_item_settings_changed(self, task_id: str, settings: dict):
        """Handle item settings changed."""
        task = self.download_manager.get_task(task_id)
        if task:
            task.selected_itag = settings.get('itag', task.selected_itag)
            task.audio_only = settings.get('audio_only', task.audio_only)
            task.download_subtitles = settings.get('subtitles', task.download_subtitles)

    def _on_download_progress(self, task_id: str, percentage: float):
        """Handle download progress update."""
        if task_id in self.video_widgets:
            self.video_widgets[task_id].set_progress(percentage)

    def _on_download_status(self, task_id: str, status: DownloadStatus):
        """Handle download status change."""
        if task_id in self.video_widgets:
            self.video_widgets[task_id].set_status(status)

    def _on_download_finished(self, task_id: str, file_path: str):
        """Handle download finished."""
        if task_id in self.video_widgets:
            self.video_widgets[task_id].set_status(DownloadStatus.COMPLETED)
        self.status_label.setText(f"Completed: {os.path.basename(file_path)}")

    def _on_download_error(self, task_id: str, error: str):
        """Handle download error."""
        if task_id in self.video_widgets:
            self.video_widgets[task_id].set_error(error)

    def _on_queue_status(self, downloading: int, queued: int):
        """Handle queue status update."""
        if downloading == 0 and queued == 0:
            self.status_label.setText("Ready")
        else:
            self.status_label.setText(f"{downloading} downloading, {queued} queued")

    def _on_download_all(self):
        """Download all pending items."""
        self.download_manager.start_all()

    def _on_clear_list(self):
        """Clear all items from the list."""
        reply = QMessageBox.question(
            self,
            "Clear List",
            "Remove all videos from the list?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for task_id in list(self.video_widgets.keys()):
                self._on_item_remove(task_id)

    def _on_open_folder(self):
        """Open the download folder."""
        folder = self.settings['download_folder']
        if os.path.exists(folder):
            os.startfile(folder)
        else:
            QMessageBox.warning(self, "Error", f"Folder not found: {folder}")

    def _on_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.settings, self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _on_settings_changed(self, new_settings: dict):
        """Handle settings changed."""
        old_dark_mode = self.settings.get('dark_mode', True)
        self.settings.update(new_settings)
        self._save_settings()

        # Apply changes
        self.download_manager.set_output_path(self.settings['download_folder'])
        self.download_manager.max_concurrent = self.settings['concurrent_downloads']

        # Apply theme if changed
        if new_settings.get('dark_mode') != old_dark_mode:
            self._apply_theme()

        self.status_label.setText("Settings saved")

    def closeEvent(self, event):
        """Handle window close."""
        # Cancel any running downloads
        for task_id in list(self.video_widgets.keys()):
            self.download_manager.cancel_task(task_id)

        self._save_settings()
        event.accept()
