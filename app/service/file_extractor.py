from pathlib import Path
import fitz


def read_txt(file_path: str) -> str:
    path = Path(file_path)
    return path.read_text(encoding="utf-8")


def read_pdf(file_path: str) -> str:
    text_parts = []
    doc = fitz.open(file_path)

    for page in doc:
        text_parts.append(page.get_text())

    doc.close()
    return "\n".join(text_parts)


def extract_text(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == ".txt":
        return read_txt(file_path)
    elif extension == ".pdf":
        return read_pdf(file_path)
    else:
        raise ValueError("Format non supporté")