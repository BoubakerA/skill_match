import fitz  
import pytesseract
from PIL import Image


def extract_text_pymupdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    return text.strip()


def is_valid_text(text: str, min_chars: int = 50) -> bool:
    if not text:
        return False

    cleaned = text.replace("\n", "").strip()
    return len(cleaned) > min_chars

def extract_text_ocr(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # upscale for better OCR
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        text += pytesseract.image_to_string(img) + "\n"

    return text.strip()


def extract_pdf_text(pdf_path: str) -> str:
    """
    Hybrid PDF text extractor:
    - Try PyMuPDF (fast)
    - If text is weak → OCR fallback
    """

    text = extract_text_pymupdf(pdf_path)

    if is_valid_text(text):
        print("✅ Digital PDF detected (PyMuPDF used)")
        return text
    else:
        print("⚠️ Scanned PDF detected (OCR fallback)")
        return extract_text_ocr(pdf_path)


# -----------------------------
# 5. Example usage
# -----------------------------
if __name__ == "__main__":
    pdf_path = "cv.pdf"
    text = extract_pdf_text(pdf_path)

    print("\n--- EXTRACTED TEXT ---\n")
    print(text)