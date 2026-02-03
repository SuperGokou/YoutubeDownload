"""Video information fetching module."""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from pytubefix import YouTube, Playlist
import requests
from io import BytesIO

from .utils import format_size, format_duration, is_playlist_url


@dataclass
class StreamInfo:
    """Information about a video stream."""
    itag: int
    resolution: str
    mime_type: str
    filesize: int
    is_progressive: bool  # Contains both audio and video
    is_audio_only: bool
    abr: str = ""  # Audio bitrate for audio streams

    @property
    def display_name(self) -> str:
        """Get display name for dropdown."""
        if self.is_audio_only:
            return f"Audio {self.abr}"
        quality = self.resolution or "Unknown"
        fmt = self.mime_type.split('/')[-1].upper() if self.mime_type else "MP4"
        size = format_size(self.filesize) if self.filesize else ""
        prog = "" if self.is_progressive else " (video only)"
        return f"{quality} {fmt}{prog} - {size}"


@dataclass
class CaptionInfo:
    """Information about available captions."""
    code: str
    name: str


@dataclass
class VideoInfo:
    """Complete video information."""
    url: str
    video_id: str
    title: str
    author: str
    duration: int  # seconds
    thumbnail_url: str
    streams: List[StreamInfo] = field(default_factory=list)
    audio_streams: List[StreamInfo] = field(default_factory=list)
    captions: List[CaptionInfo] = field(default_factory=list)
    thumbnail_data: bytes = None

    @property
    def duration_str(self) -> str:
        return format_duration(self.duration)


class VideoInfoWorker(QThread):
    """Worker thread for fetching video information."""

    finished = pyqtSignal(object)  # VideoInfo or None
    error = pyqtSignal(str)
    progress = pyqtSignal(str)  # Status message

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            self.progress.emit("Fetching video info...")
            yt = YouTube(self.url)

            video_info = VideoInfo(
                url=self.url,
                video_id=yt.video_id,
                title=yt.title,
                author=yt.author,
                duration=yt.length,
                thumbnail_url=yt.thumbnail_url,
            )

            # Get video streams
            self.progress.emit("Analyzing streams...")
            for stream in yt.streams.filter(type="video").order_by('resolution').desc():
                stream_info = StreamInfo(
                    itag=stream.itag,
                    resolution=stream.resolution,
                    mime_type=stream.mime_type,
                    filesize=stream.filesize,
                    is_progressive=stream.is_progressive,
                    is_audio_only=False,
                )
                video_info.streams.append(stream_info)

            # Get audio streams
            for stream in yt.streams.filter(only_audio=True).order_by('abr').desc():
                stream_info = StreamInfo(
                    itag=stream.itag,
                    resolution=None,
                    mime_type=stream.mime_type,
                    filesize=stream.filesize,
                    is_progressive=False,
                    is_audio_only=True,
                    abr=stream.abr,
                )
                video_info.audio_streams.append(stream_info)

            # Get captions
            self.progress.emit("Checking subtitles...")
            for caption in yt.captions:
                caption_info = CaptionInfo(
                    code=caption.code,
                    name=caption.name,
                )
                video_info.captions.append(caption_info)

            # Fetch thumbnail
            self.progress.emit("Loading thumbnail...")
            try:
                response = requests.get(video_info.thumbnail_url, timeout=10)
                if response.status_code == 200:
                    video_info.thumbnail_data = response.content
            except Exception:
                pass  # Thumbnail is optional

            self.finished.emit(video_info)

        except Exception as e:
            self.error.emit(str(e))


class PlaylistInfoWorker(QThread):
    """Worker thread for fetching playlist information."""

    video_found = pyqtSignal(str)  # Emit each video URL
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            self.progress.emit("Loading playlist...")
            playlist = Playlist(self.url)

            total = len(playlist.video_urls)
            for i, video_url in enumerate(playlist.video_urls):
                self.progress.emit(f"Found video {i+1}/{total}")
                self.video_found.emit(video_url)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class VideoInfoFetcher(QObject):
    """Manager for fetching video information."""

    video_info_ready = pyqtSignal(object)  # VideoInfo
    playlist_video_found = pyqtSignal(str)  # URL
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._workers = []

    def fetch_url(self, url: str):
        """Fetch information for a URL (video or playlist)."""
        if is_playlist_url(url):
            worker = PlaylistInfoWorker(url)
            worker.video_found.connect(self.playlist_video_found.emit)
            worker.finished.connect(self._on_playlist_finished)
            worker.error.connect(self.error.emit)
            worker.progress.connect(self.progress.emit)
        else:
            worker = VideoInfoWorker(url)
            worker.finished.connect(self._on_video_info_ready)
            worker.error.connect(self.error.emit)
            worker.progress.connect(self.progress.emit)

        self._workers.append(worker)
        worker.start()

    def _on_video_info_ready(self, video_info):
        """Handle video info ready."""
        self.video_info_ready.emit(video_info)
        self.finished.emit()

    def _on_playlist_finished(self):
        """Handle playlist loading finished."""
        self.finished.emit()

    def cancel_all(self):
        """Cancel all running workers."""
        for worker in self._workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        self._workers.clear()
