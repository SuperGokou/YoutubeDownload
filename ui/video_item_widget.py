"""Video item widget for the download list."""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QProgressBar,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage

from core.video_info import VideoInfo, StreamInfo
from core.downloader import DownloadStatus
from core.utils import format_size


class ThumbnailLabel(QLabel):
    """Label for displaying video thumbnail."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 90)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            background-color: #3d3d3d;
            border-radius: 4px;
        """)
        self.setText("Loading...")

    def set_thumbnail(self, data: bytes):
        """Set thumbnail from image data."""
        if data:
            image = QImage.fromData(data)
            if not image.isNull():
                pixmap = QPixmap.fromImage(image)
                scaled = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
                return
        self.setText("No Preview")


class VideoItemWidget(QFrame):
    """Widget representing a single video in the download list."""

    download_clicked = pyqtSignal(str)  # task_id
    remove_clicked = pyqtSignal(str)  # task_id
    settings_changed = pyqtSignal(str, dict)  # task_id, settings

    def __init__(self, task_id: str, video_info: VideoInfo, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.video_info = video_info
        self._status = DownloadStatus.PENDING

        self.setObjectName("videoItem")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._setup_ui()
        self._populate_data()

    def _setup_ui(self):
        """Set up the widget UI."""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(16)

        # Thumbnail
        self.thumbnail = ThumbnailLabel()
        main_layout.addWidget(self.thumbnail)

        # Info section
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Title
        self.title_label = QLabel()
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumWidth(400)
        info_layout.addWidget(self.title_label)

        # Channel and duration
        self.meta_label = QLabel()
        self.meta_label.setObjectName("channelLabel")
        info_layout.addWidget(self.meta_label)

        # Progress bar (hidden initially)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.hide()
        info_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready to download")
        self.status_label.setObjectName("statusLabel")
        info_layout.addWidget(self.status_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, 1)

        # Controls section
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(8)

        # Quality dropdown
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.setMinimumWidth(180)
        self.quality_combo.currentIndexChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self.quality_combo)
        controls_layout.addLayout(quality_layout)

        # Checkboxes
        self.audio_only_check = QCheckBox("Audio only")
        self.audio_only_check.stateChanged.connect(self._on_audio_only_changed)
        controls_layout.addWidget(self.audio_only_check)

        self.subtitles_check = QCheckBox("Subtitles")
        controls_layout.addWidget(self.subtitles_check)

        controls_layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self._on_download_clicked)
        button_layout.addWidget(self.download_btn)

        self.remove_btn = QPushButton("X")
        self.remove_btn.setObjectName("dangerButton")
        self.remove_btn.setFixedWidth(32)
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        button_layout.addWidget(self.remove_btn)

        controls_layout.addLayout(button_layout)

        main_layout.addLayout(controls_layout)

    def _populate_data(self):
        """Populate widget with video data."""
        # Set title (truncate if too long)
        title = self.video_info.title
        if len(title) > 60:
            title = title[:57] + "..."
        self.title_label.setText(title)

        # Set meta info
        meta = f"{self.video_info.author} | {self.video_info.duration_str}"
        self.meta_label.setText(meta)

        # Set thumbnail
        if self.video_info.thumbnail_data:
            self.thumbnail.set_thumbnail(self.video_info.thumbnail_data)

        # Populate quality options
        self._populate_quality_options()

        # Enable/disable subtitles checkbox based on availability
        has_subtitles = len(self.video_info.captions) > 0
        self.subtitles_check.setEnabled(has_subtitles)
        if not has_subtitles:
            self.subtitles_check.setToolTip("No subtitles available")

    def _populate_quality_options(self):
        """Populate quality dropdown with available streams."""
        self.quality_combo.clear()

        # Collect all unique resolutions and sort by quality
        seen_resolutions = set()
        all_streams = []

        # First add adaptive streams (higher quality, video only - needs ffmpeg)
        for stream in self.video_info.streams:
            if not stream.is_progressive and stream.resolution:
                res_key = stream.resolution
                if res_key not in seen_resolutions:
                    seen_resolutions.add(res_key)
                    all_streams.append(stream)

        # Then add progressive streams (lower quality but has audio)
        for stream in self.video_info.streams:
            if stream.is_progressive and stream.resolution:
                res_key = f"{stream.resolution}_prog"
                if res_key not in seen_resolutions:
                    seen_resolutions.add(res_key)
                    all_streams.append(stream)

        # Sort by resolution (highest first)
        def get_res_value(s):
            if s.resolution:
                try:
                    return int(s.resolution.replace('p', ''))
                except ValueError:
                    return 0
            return 0

        all_streams.sort(key=get_res_value, reverse=True)

        # Add to combo box
        for stream in all_streams:
            self.quality_combo.addItem(stream.display_name, stream.itag)

        # Default to first item (highest quality)
        if self.quality_combo.count() > 0:
            self.quality_combo.setCurrentIndex(0)

    def _on_quality_changed(self, index):
        """Handle quality selection change."""
        self._emit_settings_changed()

    def _on_audio_only_changed(self, state):
        """Handle audio only checkbox change."""
        is_audio_only = state == Qt.CheckState.Checked.value

        # Update quality dropdown
        self.quality_combo.clear()

        if is_audio_only:
            # Show audio streams
            for stream in self.video_info.audio_streams:
                self.quality_combo.addItem(stream.display_name, stream.itag)
        else:
            # Show video streams
            self._populate_quality_options()

        self._emit_settings_changed()

    def _emit_settings_changed(self):
        """Emit settings changed signal."""
        settings = {
            'itag': self.quality_combo.currentData(),
            'audio_only': self.audio_only_check.isChecked(),
            'subtitles': self.subtitles_check.isChecked(),
        }
        self.settings_changed.emit(self.task_id, settings)

    def _on_download_clicked(self):
        """Handle download button click."""
        self.download_clicked.emit(self.task_id)

    def _on_remove_clicked(self):
        """Handle remove button click."""
        self.remove_clicked.emit(self.task_id)

    def set_status(self, status: DownloadStatus):
        """Update the status display."""
        self._status = status

        status_texts = {
            DownloadStatus.PENDING: "Ready to download",
            DownloadStatus.DOWNLOADING: "Downloading...",
            DownloadStatus.COMPLETED: "Completed",
            DownloadStatus.ERROR: "Error",
            DownloadStatus.CANCELLED: "Cancelled",
        }

        self.status_label.setText(f"Status: {status_texts.get(status, 'Unknown')}")

        # Show/hide progress bar
        self.progress_bar.setVisible(status == DownloadStatus.DOWNLOADING)

        # Update button states
        if status == DownloadStatus.DOWNLOADING:
            self.download_btn.setText("Cancel")
            self.download_btn.setEnabled(True)
            self.quality_combo.setEnabled(False)
            self.audio_only_check.setEnabled(False)
        elif status == DownloadStatus.COMPLETED:
            self.download_btn.setText("Done")
            self.download_btn.setEnabled(False)
            self.quality_combo.setEnabled(False)
            self.audio_only_check.setEnabled(False)
        elif status == DownloadStatus.ERROR:
            self.download_btn.setText("Retry")
            self.download_btn.setEnabled(True)
            self.quality_combo.setEnabled(True)
            self.audio_only_check.setEnabled(True)
        else:
            self.download_btn.setText("Download")
            self.download_btn.setEnabled(True)
            self.quality_combo.setEnabled(True)
            self.audio_only_check.setEnabled(True)

    def set_progress(self, percentage: float):
        """Update the progress bar."""
        self.progress_bar.setValue(int(percentage))
        self.status_label.setText(f"Status: Downloading... {percentage:.1f}%")

    def set_error(self, message: str):
        """Display error message."""
        self.set_status(DownloadStatus.ERROR)
        short_msg = message[:50] + "..." if len(message) > 50 else message
        self.status_label.setText(f"Error: {short_msg}")
        self.status_label.setToolTip(message)

    def get_selected_itag(self) -> int:
        """Get the selected stream itag."""
        return self.quality_combo.currentData()

    def is_audio_only(self) -> bool:
        """Check if audio only is selected."""
        return self.audio_only_check.isChecked()

    def wants_subtitles(self) -> bool:
        """Check if subtitles are requested."""
        return self.subtitles_check.isChecked()
