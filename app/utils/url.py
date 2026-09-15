from urllib.parse import urlparse

def is_valid_youtube_url(url: str) -> bool:
    """Validates if the provided string is a valid YouTube URL."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False
            
        valid_domains = [
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
            "youtu.be"
        ]
        
        if parsed.netloc not in valid_domains:
            return False
            
        return True
    except Exception:
        return False
