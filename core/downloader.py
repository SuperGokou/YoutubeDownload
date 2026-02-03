"""Download manager with threading support."""

import os
import subprocess
import shutil
from typing import Optional, Callable
from PyQt6.QtCore import QThread, pyqtSignal, QObject, QMutex, QWaitCondition
from pytubefix import YouTube
from dataclasses import dataclass
from enum import Enum, auto

from .video_info import VideoInfo
from .utils import sanitize_filename, get_download_folder


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    return shutil.which('ffmpeg') is not None


class DownloadStatus(Enum):
    PENDING = auto()
    DOWNLOADING = auto()
    COMPLETED = auto()
    ERROR = auto()
    CANCELLED = auto()


@dataclass
class DownloadTask:
    """A download task configuration."""
    video_info: VideoInfo
    output_path: str
    selected_itag: int
    audio_only: bool = False
    download_subtitles: bool = False
    subtitle_lang: str = "en"
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    downloaded_path: str = ""


class DownloadWorker(QThread):
    """Worker thread for downloading a single video."""

    progress = pyqtSignal(str, float)  # task_id, percentage
    status_changed = pyqtSignal(str, object)  # task_id, DownloadStatus
    speed_update = pyqtSignal(str, str)  # task_id, speed string
    finished = pyqtSignal(str, str)  # task_id, file_path
    error = pyqtSignal(str, str)  # task_id, error_message

    def __init__(self, task_id: str, task: DownloadTask, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.task = task
        self._cancelled = False
        self._bytes_received = 0
        self._total_bytes = 0

    def run(self):
        try:
            self.status_changed.emit(self.task_id, DownloadStatus.DOWNLOADING)

            yt = YouTube(
                self.task.video_info.url,
                on_progress_callback=self._on_progress,
            )

            # Prepare base filename
            base_filename = sanitize_filename(self.task.video_info.title)

            # Select the stream
            if self.task.audio_only:
                stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                if not stream:
                    raise Exception("No audio stream available")

                filename = base_filename + ".mp3"
                self._total_bytes = stream.filesize or 0
                output_path = stream.download(
                    output_path=self.task.output_path,
                    filename=filename,
                )
            else:
                stream = yt.streams.get_by_itag(self.task.selected_itag)
                if not stream:
                    raise Exception("Selected stream not available")

                # Check if this is an adaptive stream (video only, no audio)
                if not stream.is_progressive:
                    # Need to download video and audio separately, then merge
                    if not check_ffmpeg():
                        raise Exception("FFmpeg required for high-quality downloads. Please install FFmpeg and add it to PATH.")

                    # Download video stream
                    video_filename = base_filename + "_video_temp.mp4"
                    self._total_bytes = (stream.filesize or 0) * 2  # Estimate for both
                    video_path = stream.download(
                        output_path=self.task.output_path,
                        filename=video_filename,
                    )

                    if self._cancelled:
                        self._cleanup_temp_files(video_path)
                        self.status_changed.emit(self.task_id, DownloadStatus.CANCELLED)
                        return

                    # Download best audio stream
                    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
                    if not audio_stream:
                        self._cleanup_temp_files(video_path)
                        raise Exception("No audio stream available for merging")

                    audio_filename = base_filename + "_audio_temp.mp4"
                    audio_path = audio_stream.download(
                        output_path=self.task.output_path,
                        filename=audio_filename,
                    )

                    if self._cancelled:
                        self._cleanup_temp_files(video_path, audio_path)
                        self.status_changed.emit(self.task_id, DownloadStatus.CANCELLED)
                        return

                    # Merge with ffmpeg
                    output_filename = base_filename + ".mp4"
                    output_path = os.path.join(self.task.output_path, output_filename)

                    # Remove existing output file if exists
                    if os.path.exists(output_path):
                        os.remove(output_path)

                    merge_cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-i', audio_path,
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        output_path
                    ]

                    result = subprocess.run(
                        merge_cmd,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                    )

                    # Clean up temp files
                    self._cleanup_temp_files(video_path, audio_path)

                    if result.returncode != 0:
                        raise Exception(f"FFmpeg merge failed: {result.stderr[:200]}")

                else:
                    # Progressive stream - direct download
                    ext = stream.mime_type.split('/')[-1] if stream.mime_type else 'mp4'
                    filename = base_filename + f".{ext}"
                    self._total_bytes = stream.filesize or 0
                    output_path = stream.download(
                        output_path=self.task.output_path,
                        filename=filename,
                    )

            # Download subtitles if requested
            if self.task.download_subtitles and self.task.video_info.captions:
                self._download_subtitles(yt, output_path)

            if self._cancelled:
                self.status_changed.emit(self.task_id, DownloadStatus.CANCELLED)
                return

            self.status_changed.emit(self.task_id, DownloadStatus.COMPLETED)
            self.finished.emit(self.task_id, output_path)

        except Exception as e:
            self.status_changed.emit(self.task_id, DownloadStatus.ERROR)
            self.error.emit(self.task_id, str(e))

    def _cleanup_temp_files(self, *paths):
        """Remove temporary files."""
        for path in paths:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def _on_progress(self, stream, chunk, bytes_remaining):
        """Progress callback from pytube."""
        if self._cancelled:
            raise Exception("Download cancelled")

        total = stream.filesize
        downloaded = total - bytes_remaining
        percentage = (downloaded / total) * 100 if total else 0
        self.progress.emit(self.task_id, percentage)

    def _download_subtitles(self, yt: YouTube, video_path: str):
        """Download subtitles for the video."""
        try:
            # Try to get requested language, fall back to first available
            caption = None
            for cap in yt.captions:
                if cap.code == self.task.subtitle_lang or cap.code.startswith(self.task.subtitle_lang):
                    caption = cap
                    break

            if not caption and yt.captions:
                caption = yt.captions[0]

            if caption:
                srt_content = caption.generate_srt_captions()
                srt_path = os.path.splitext(video_path)[0] + ".srt"
                with open(srt_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
        except Exception:
            pass  # Subtitle download is optional

    def cancel(self):
        """Cancel the download."""
        self._cancelled = True


class DownloadManager(QObject):
    """Manages download queue and workers."""

    task_added = pyqtSignal(str, object)  # task_id, DownloadTask
    task_progress = pyqtSignal(str, float)  # task_id, percentage
    task_status = pyqtSignal(str, object)  # task_id, DownloadStatus
    task_finished = pyqtSignal(str, str)  # task_id, file_path
    task_error = pyqtSignal(str, str)  # task_id, error_message
    queue_status = pyqtSignal(int, int)  # downloading_count, queued_count

    def __init__(self, max_concurrent: int = 2, parent=None):
        super().__init__(parent)
        self.max_concurrent = max_concurrent
        self.output_path = get_download_folder()

        self._tasks: dict[str, DownloadTask] = {}
        self._workers: dict[str, DownloadWorker] = {}
        self._queue: list[str] = []  # task_ids waiting to download
        self._task_counter = 0
        self._mutex = QMutex()

    def add_task(self, video_info: VideoInfo, itag: int, audio_only: bool = False,
                 subtitles: bool = False, subtitle_lang: str = "en") -> str:
        """Add a new download task. Returns task_id."""
        self._mutex.lock()
        try:
            self._task_counter += 1
            task_id = f"task_{self._task_counter}"

            task = DownloadTask(
                video_info=video_info,
                output_path=self.output_path,
                selected_itag=itag,
                audio_only=audio_only,
                download_subtitles=subtitles,
                subtitle_lang=subtitle_lang,
            )

            self._tasks[task_id] = task
            self._queue.append(task_id)

            self.task_added.emit(task_id, task)
            self._update_queue_status()

            return task_id
        finally:
            self._mutex.unlock()

    def start_task(self, task_id: str):
        """Start downloading a specific task."""
        if task_id not in self._tasks:
            return

        if task_id in self._workers and self._workers[task_id].isRunning():
            return  # Already downloading

        task = self._tasks[task_id]
        if task.status == DownloadStatus.COMPLETED:
            return  # Already completed

        # Check concurrent limit
        running_count = sum(1 for w in self._workers.values() if w.isRunning())
        if running_count >= self.max_concurrent:
            # Add to queue if not already there
            if task_id not in self._queue:
                self._queue.append(task_id)
            return

        # Remove from queue if present
        if task_id in self._queue:
            self._queue.remove(task_id)

        # Create and start worker
        worker = DownloadWorker(task_id, task)
        worker.progress.connect(self._on_progress)
        worker.status_changed.connect(self._on_status_changed)
        worker.finished.connect(self._on_finished)
        worker.error.connect(self._on_error)

        self._workers[task_id] = worker
        worker.start()
        self._update_queue_status()

    def start_all(self):
        """Start downloading all pending tasks."""
        for task_id, task in self._tasks.items():
            if task.status == DownloadStatus.PENDING:
                self.start_task(task_id)

    def cancel_task(self, task_id: str):
        """Cancel a download task."""
        if task_id in self._workers:
            self._workers[task_id].cancel()

        if task_id in self._queue:
            self._queue.remove(task_id)

        if task_id in self._tasks:
            self._tasks[task_id].status = DownloadStatus.CANCELLED
            self.task_status.emit(task_id, DownloadStatus.CANCELLED)

        self._update_queue_status()

    def remove_task(self, task_id: str):
        """Remove a task from the manager."""
        self.cancel_task(task_id)

        if task_id in self._tasks:
            del self._tasks[task_id]
        if task_id in self._workers:
            del self._workers[task_id]

        self._update_queue_status()

    def clear_completed(self):
        """Remove all completed tasks."""
        to_remove = [
            tid for tid, task in self._tasks.items()
            if task.status == DownloadStatus.COMPLETED
        ]
        for task_id in to_remove:
            self.remove_task(task_id)

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def set_output_path(self, path: str):
        """Set the download output path."""
        self.output_path = path
        os.makedirs(path, exist_ok=True)

    def _on_progress(self, task_id: str, percentage: float):
        """Handle progress update from worker."""
        if task_id in self._tasks:
            self._tasks[task_id].progress = percentage
        self.task_progress.emit(task_id, percentage)

    def _on_status_changed(self, task_id: str, status: DownloadStatus):
        """Handle status change from worker."""
        if task_id in self._tasks:
            self._tasks[task_id].status = status
        self.task_status.emit(task_id, status)
        self._update_queue_status()

    def _on_finished(self, task_id: str, file_path: str):
        """Handle download finished."""
        if task_id in self._tasks:
            self._tasks[task_id].downloaded_path = file_path
        self.task_finished.emit(task_id, file_path)
        self._process_queue()

    def _on_error(self, task_id: str, error_message: str):
        """Handle download error."""
        if task_id in self._tasks:
            self._tasks[task_id].error_message = error_message
        self.task_error.emit(task_id, error_message)
        self._process_queue()

    def _process_queue(self):
        """Process the next item in the queue."""
        running_count = sum(1 for w in self._workers.values() if w.isRunning())

        while self._queue and running_count < self.max_concurrent:
            task_id = self._queue.pop(0)
            if task_id in self._tasks and self._tasks[task_id].status == DownloadStatus.PENDING:
                self.start_task(task_id)
                running_count += 1

        self._update_queue_status()

    def _update_queue_status(self):
        """Emit queue status update."""
        downloading = sum(
            1 for task in self._tasks.values()
            if task.status == DownloadStatus.DOWNLOADING
        )
        queued = sum(
            1 for task in self._tasks.values()
            if task.status == DownloadStatus.PENDING
        )
        self.queue_status.emit(downloading, queued)
