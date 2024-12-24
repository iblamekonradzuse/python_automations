"""
YouTube Content Downloader

Downloads audio or video using yt-dlp.
Tried not to use any libary heavy tools.
I personally limited the video quality to 1080p and audio to M4A format, but you can customize it.

Usage:
    python youtube_download.py <youtube_url> [audio (if you want the audio only)]

    example: python youtube_download.py https://www.youtube.com/watch?v=xvFZjo5PgG0 
    example: python youtube_download.py https://www.youtube.com/watch?v=xvFZjo5PgG0 audio
"""

from sys import argv
import yt_dlp
import os

# Define base download paths
BASE_VIDEO_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "youtube_videos")
BASE_AUDIO_PATH = os.path.join(os.path.expanduser("~"), "Downloads", "youtube_audio")

def ensure_download_directories():
    """
    Create download directories if they don't exist.
    
    Creates two directories:
    - ~/Downloads/youtube_videos: For video content
    - ~/Downloads/youtube_audio: For audio content
    """
    os.makedirs(BASE_VIDEO_PATH, exist_ok=True)
    os.makedirs(BASE_AUDIO_PATH, exist_ok=True)

def download_content(url, download_type="video"):
    """
    Download YouTube content with comprehensive error handling.
    
    Args:
        url (str): YouTube video URL to download from
        download_type (str): Content type to download:
            - "video": Downloads MP4 video (default)
            - "audio": Extracts audio in M4A format
    
    Video download specifications:
    - Maximum resolution: 1080p
    - Container format: MP4
    - Requires both video and audio streams
    - Prioritizes quality based on: resolution → format → audio presence
    
    Audio download specifications:
    - Format: M4A (YouTube format ID: 140)
    - Extracts audio-only stream
    """
    try:
        ensure_download_directories()
        
        # Configure yt-dlp options
        if download_type == "video":
            output_path = os.path.join(BASE_VIDEO_PATH, '%(title)s.%(ext)s')
            ydl_opts = {
                'format': 'bv*[height<=1080][ext=mp4][acodec!=none]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best[height<=1080]',
                'outtmpl': output_path,
                'quiet': False,
                'no_warnings': False,
                'format_sort': ['res:1080', 'ext:mp4:m4a', 'hasaud'],
                'merge_output_format': None  # Prevent merging attempts
            }
        else:  # audio
            output_path = os.path.join(BASE_AUDIO_PATH, '%(title)s.%(ext)s')
            ydl_opts = {
                'format': '140',  # This is YouTube's audio-only format ID
                'outtmpl': output_path,
                'quiet': False,
                'no_warnings': False,
                'extract_audio': True,
            }

        print(f"\nFetching content from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video information first
            info = ydl.extract_info(url, download=False)
            print(f"\nTitle: {info.get('title', 'Unknown')}")
            print(f"Duration: {info.get('duration', 'Unknown')} seconds")
            
            if download_type == "video":
                formats = info.get('formats', [])
                # Find the best format that meets our criteria
                selected_format = next(
                    (f for f in formats 
                     if f.get('ext') == 'mp4' 
                     and f.get('acodec') != 'none' 
                     and f.get('vcodec') != 'none'
                     and (f.get('height') or 0) <= 1080),
                    None
                )
                if selected_format:
                    print(f"Selected quality: {selected_format.get('height', 'Unknown')}p")
            else:
                print("Downloading audio (M4A format)")
                
            # Download the content
            print("\nStarting download...")
            ydl.download([url])
            
        print("\nDownload completed successfully!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify the video URL is correct and accessible")
        print("3. Ensure you have write permissions in the Downloads directory")
        print("4. Make sure yt-dlp is installed: pip install -U yt-dlp")

if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: python youtube_download.py <youtube_url> [video|audio]")
        print("Default is video if no type specified")
        exit(1)
    
    url = argv[1]
    download_type = argv[2].lower() if len(argv) > 2 else "video"
    
    if download_type not in ["video", "audio"]:
        print("Error: Second argument must be either 'video' or 'audio'")
        exit(1)
        
    download_content(url, download_type)
