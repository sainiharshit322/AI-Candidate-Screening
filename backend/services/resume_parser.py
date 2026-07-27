import httpx
import pdfplumber
import io
from docx import Document

async def download_and_parse_resume(url: str) -> str:
    if not url:
        return ""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return ""
            content_type = r.headers.get("content-type", "").lower()
            data = r.content
            if "pdf" in content_type or url.lower().endswith(".pdf"):
                with pdfplumber.open(io.BytesIO(data)) as pdf:
                    return "\n".join(p.extract_text() or "" for p in pdf.pages)
            elif "word" in content_type or "officedocument" in content_type or url.lower().endswith(".docx"):
                doc = Document(io.BytesIO(data))
                return "\n".join(p.text for p in doc.paragraphs)
            else:
                try:
                    return r.text[:5000]
                except Exception:
                    return ""
    except Exception as e:
        print(f"Error parsing resume from {url}: {e}")
        return ""
