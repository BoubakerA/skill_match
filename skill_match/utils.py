def read_uploaded_file(file) -> str:
    raw = file.read()
    for encoding in ["utf-8", "windows-1252", "latin-1"]:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")