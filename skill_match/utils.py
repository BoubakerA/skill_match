import re
import fitz  
import filetype
import pytesseract
import tempfile, os
from PIL import Image

def read_uploaded_file(file) -> str:
    raw = file.read()
    kind = filetype.guess(raw)
    mime = kind.mime if kind else "text/plain"

    if mime == "application/pdf":
        # Write to a temp file, then use your existing PDF extractor
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(raw)
            tmp_path = tmp.name
        try:
            return extract_pdf_text(tmp_path)
        finally:
            os.unlink(tmp_path)

    elif mime and mime.startswith("text/"):
        # Text files: try encodings in order of likelihood
        for encoding in ["utf-8", "windows-1252", "latin-1"]:
            try:
                return raw.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw.decode("utf-8", errors="replace")  # Final fallback

    else:
        raise ValueError(f"Unsupported file type: {mime}")


def clean_pdf_text(text: str) -> str:
    # Remove lone non-alphanumeric/punctuation characters (icon artifacts)
    text = re.sub(r'(?<!\w)[^\w\s,.\-@:/éèêëàâùûüôîïç«»œ]+(?!\w)', '', text)
    # Normalize multiple spaces/newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_text_pymupdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"
    
    return clean_pdf_text(text)


def is_valid_text(text: str, min_chars: int = 50) -> bool:
    if not text:
        return False

    cleaned = text.replace("\n", "").strip()
    return len(cleaned) > min_chars
    

def extract_text_ocr(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        text += pytesseract.image_to_string(img) + "\n"

    return clean_pdf_text(text)

def extract_pdf_text(pdf_path: str) -> str:

    text = extract_text_pymupdf(pdf_path)

    if is_valid_text(text):
        print("✅ Digital PDF detected (PyMuPDF used)")
        return text
    else:
        print("⚠️ Scanned PDF detected (OCR fallback)")
        return extract_text_ocr(pdf_path)