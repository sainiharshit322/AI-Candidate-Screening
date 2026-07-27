import httpx
import pdfplumber
import io
import re
from docx import Document

def transform_google_drive_url(url: str) -> str:
    if not url:
        return ""
    # Extract file ID from google drive links like /file/d/<file_id>/view or id=<file_id>
    if "drive.google.com" in url or "docs.google.com" in url:
        match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', url)
        if not match:
            match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
        if match:
            file_id = match.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return url

async def download_and_parse_resume(url: str) -> str:
    if not url:
        return ""
    
    download_url = transform_google_drive_url(url)
    
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(download_url)
            if r.status_code != 200:
                # Retry with original URL if transformed URL returned non-200
                r = await client.get(url)
                if r.status_code != 200:
                    return ""
                    
            content_type = r.headers.get("content-type", "").lower()
            data = r.content
            
            # Try PDF first
            try:
                with pdfplumber.open(io.BytesIO(data)) as pdf:
                    text = "\n".join(p.extract_text() or "" for p in pdf.pages)
                    if text.strip():
                        return text
            except Exception:
                pass
                
            # Try DOCX
            try:
                doc = Document(io.BytesIO(data))
                text = "\n".join(p.text for p in doc.paragraphs)
                if text.strip():
                    return text
            except Exception:
                pass

            # Text fallback
            try:
                txt = r.text[:5000]
                if "<html" not in txt.lower():
                    return txt
            except Exception:
                pass
                
            return ""
    except Exception as e:
        print(f"Error parsing resume from {url}: {e}")
        return ""
