import re

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to make it safe for most operating systems.
    Removes path traversal characters and unsafe characters.
    """
    if not filename:
        return "audio.mp3"
        
    # Remove path traversal characters
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")
    
    # Keep alphanumeric, spaces, dashes, underscores, and dots
    filename = re.sub(r'[^a-zA-Z0-9 \-_.]', '', filename)
    
    # Squeeze multiple spaces
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    if not filename:
        return "audio.mp3"
        
    return filename
