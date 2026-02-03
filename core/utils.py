"""Utility functions for YouTube downloader."""

import re
import os


def format_size(bytes_size: int) -> str:
    """Format bytes into human readable string."""
    if bytes_size is None:
        return "Unknown"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def format_duration(seconds: int) -> str:
    """Format seconds into HH:MM:SS or MM:SS string."""
    if seconds is None:
        return "Unknown"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    # Remove characters that are invalid in Windows filenames
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized or "untitled"


def get_download_folder() -> str:
    """Get default download folder path."""
    # Default to user's Downloads folder
    downloads = os.path.join(os.path.expanduser("~"), "Downloads", "YouTubeDownloads")
    os.makedirs(downloads, exist_ok=True)
    return downloads


def parse_urls(text: str) -> list:
    """Parse text to extract YouTube URLs."""
    # Pattern to match YouTube video and playlist URLs
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&[^\s]*)?',
        r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/[\w-]+',
    ]

    urls = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        urls.extend(matches)

    # Ensure URLs have https:// prefix
    cleaned_urls = []
    for url in urls:
        if not url.startswith('http'):
            url = 'https://' + url
        if url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_playlist_url(url: str) -> bool:
    """Check if URL is a playlist URL."""
    return 'playlist?list=' in url or '&list=' in url
