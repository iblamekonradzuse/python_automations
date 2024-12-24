#!/usr/bin/env python3
"""
Downloads Folder Organizer
-------------------------

This script automatically organizes files in a downloads directory by monitoring for changes
and moving files to appropriate subdirectories based on their file extensions.

Requirements:
- watchdog library (`pip install watchdog`)
- Python 3.6+

Usage:
1. Modify the source and destination directory paths as needed
2. Run the script: `python3 downloads_organizer.py`
3. The script will continue running until interrupted with Ctrl+C
"""

from os import scandir, rename, makedirs
from os.path import splitext, exists, join
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration: Directory paths
# Modify these paths according to your system setup
source_dir = "/Users/wervand/Downloads"
dest_dir_sfx = "/Users/wervand/Downloads/sfx"
dest_dir_music = "/Users/wervand/Downloads/music"
dest_dir_video = "/Users/wervand/Downloads/video"
dest_dir_image = "/Users/wervand/Downloads/image"
dest_dir_documents = "/Users/wervand/Downloads/documents"
dest_dir_python = "/Users/wervand/Downloads/python"
dest_dir_rust = "/Users/wervand/Downloads/rust"
dest_dir_markdown = "/Users/wervand/Downloads/markdown"
dest_dir_apps = "/Users/wervand/Downloads/apps"
dest_dir_books = "/Users/wervand/Downloads/books"
dest_dir_archives = "/Users/wervand/Downloads/archives"
dest_dir_web = "/Users/wervand/Downloads/web"
dest_dir_other = "/Users/wervand/Downloads/other"
dest_dir_folders = "/Users/wervand/Downloads/folders"  # For organizing downloaded folders

def create_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        source_dir,
        dest_dir_sfx,
        dest_dir_music,
        dest_dir_video,
        dest_dir_image,
        dest_dir_documents,
        dest_dir_python,
        dest_dir_rust,
        dest_dir_markdown,
        dest_dir_apps,
        dest_dir_books,
        dest_dir_archives,
        dest_dir_web,
        dest_dir_other,
        dest_dir_folders
    ]
    
    for directory in directories:
        if not exists(directory):
            makedirs(directory)
            logging.info(f"Created directory: {directory}")

# File extension definitions
# Add or modify extensions as needed for your use case
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]
markdown_extensions = [".md", ".markdown"]
app_extensions = [".app", ".dmg", ".pkg", ".exe"]
rust_extensions = [".rs"]
python_extensions = [".py", ".ipynb"]
book_extensions = [".epub", ".mobi"]
archive_extensions = [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"]
web_extensions = [".html", ".htm", ".css", ".js", ".php", ".asp", ".jsx", ".tsx"]

def make_unique(dest, name):
    """
    Generate a unique filename by adding a counter if the file already exists.
    
    Args:
        dest (str): Destination directory path
        name (str): Original filename
    
    Returns:
        str: Unique filename
    """
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

def move_file(dest, entry, name):
    """
    Move a file to its destination directory, handling duplicates.
    
    Args:
        dest (str): Destination directory path
        entry: File entry object
        name (str): Filename
    """
    try:
        if exists(f"{dest}/{name}"):
            unique_name = make_unique(dest, name)
            oldName = join(dest, name)
            newName = join(dest, unique_name)
            rename(oldName, newName)
        move(entry, dest)
        logging.info(f"Successfully moved {name} to {dest}")
    except Exception as e:
        logging.error(f"Error moving {name}: {str(e)}")

class MoverHandler(FileSystemEventHandler):
    """
    Handler for file system events.
    Monitors the downloads directory and moves files to appropriate locations based on their type.
    """
    
    def on_modified(self, event):
        """
        Handle file system modification events.
        
        Args:
            event: The file system event that triggered this handler
        """
        logging.info(f"Change detected: {event.src_path}")
        try:
            with scandir(source_dir) as entries:
                for entry in entries:
                    name = entry.name
                    logging.info(f"Processing: {name}")
                    
                    # Skip the destination directories themselves
                    if entry.path in [dest_dir_sfx, dest_dir_music, dest_dir_video, dest_dir_image,
                                    dest_dir_documents, dest_dir_python, dest_dir_rust, dest_dir_markdown,
                                    dest_dir_apps, dest_dir_books, dest_dir_archives, dest_dir_web,
                                    dest_dir_other, dest_dir_folders]:
                        continue
                    
                    # Handle directories first
                    if entry.is_dir():
                        move_file(dest_dir_folders, entry, name)
                        continue
                    
                    # Process files based on their extensions
                    if entry.is_file():
                        if not any([
                            self.check_audio_files(entry, name),
                            self.check_video_files(entry, name),
                            self.check_image_files(entry, name),
                            self.check_document_files(entry, name),
                            self.check_python_files(entry, name),
                            self.check_rust_files(entry, name),
                            self.check_markdown_files(entry, name),
                            self.check_app_files(entry, name),
                            self.check_book_files(entry, name),
                            self.check_archive_files(entry, name),
                            self.check_web_files(entry, name)
                        ]):
                            # Move to 'other' if no category matches
                            move_file(dest_dir_other, entry, name)
        except Exception as e:
            logging.error(f"Error in on_modified: {str(e)}")

    def check_audio_files(self, entry, name):
        """Check for audio files and move them to appropriate directory based on size and name."""
        for audio_extension in audio_extensions:
            if name.lower().endswith(audio_extension.lower()):
                # Files smaller than 10MB or with 'SFX' in name go to sfx directory
                if entry.stat().st_size < 10_000_000 or "SFX" in name:
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move_file(dest, entry, name)
                return True
        return False

    def check_video_files(self, entry, name):
        """Check for video files and move them to the video directory."""
        for video_extension in video_extensions:
            if name.lower().endswith(video_extension.lower()):
                move_file(dest_dir_video, entry, name)
                return True
        return False

    def check_image_files(self, entry, name):
        """Check for image files and move them to the image directory."""
        for image_extension in image_extensions:
            if name.lower().endswith(image_extension.lower()):
                move_file(dest_dir_image, entry, name)
                return True
        return False

    def check_document_files(self, entry, name):
        """Check for document files and move them to the documents directory."""
        for documents_extension in document_extensions:
            if name.lower().endswith(documents_extension.lower()):
                move_file(dest_dir_documents, entry, name)
                return True
        return False

    def check_python_files(self, entry, name):
        """Check for Python files and move them to the python directory."""
        for python_extension in python_extensions:
            if name.lower().endswith(python_extension.lower()):
                move_file(dest_dir_python, entry, name)
                return True
        return False

    def check_rust_files(self, entry, name):
        """Check for Rust files and move them to the rust directory."""
        for rust_extension in rust_extensions:
            if name.lower().endswith(rust_extension.lower()):
                move_file(dest_dir_rust, entry, name)
                return True
        return False

    def check_markdown_files(self, entry, name):
        """Check for Markdown files and move them to the markdown directory."""
        for markdown_extension in markdown_extensions:
            if name.lower().endswith(markdown_extension.lower()):
                move_file(dest_dir_markdown, entry, name)
                return True
        return False

    def check_app_files(self, entry, name):
        """Check for application files and move them to the apps directory."""
        for app_extension in app_extensions:
            if name.lower().endswith(app_extension.lower()):
                move_file(dest_dir_apps, entry, name)
                return True
        return False

    def check_book_files(self, entry, name):
        """Check for book files and move them to the books directory."""
        for book_extension in book_extensions:
            if name.lower().endswith(book_extension.lower()):
                move_file(dest_dir_books, entry, name)
                return True
        return False

    def check_archive_files(self, entry, name):
        """Check for archive files and move them to the archives directory."""
        for archive_extension in archive_extensions:
            if name.lower().endswith(archive_extension.lower()):
                move_file(dest_dir_archives, entry, name)
                return True
        return False

    def check_web_files(self, entry, name):
        """Check for web development files and move them to the web directory."""
        for web_extension in web_extensions:
            if name.lower().endswith(web_extension.lower()):
                move_file(dest_dir_web, entry, name)
                return True
        return False

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create necessary directories
    create_directories()
    
    # Set up and start the file system observer
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    logging.info(f"Started monitoring {source_dir}")
    
    # Keep the script running until interrupted
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Stopping the observer...")
    observer.join()
