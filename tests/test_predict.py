import io
import pytest
from unittest.mock import MagicMock, patch

from skill_match.utils import (
    read_uploaded_file,
    clean_pdf_text,
    is_valid_text,
    extract_pdf_text,
)


class TestIsValidText:
    def test_returns_false_for_empty_string(self):
        assert is_valid_text("") is False

    def test_returns_false_for_none(self):
        assert is_valid_text(None) is False

    def test_returns_false_for_short_text(self):
        assert is_valid_text("too short") is False

    def test_returns_true_for_long_enough_text(self):
        assert is_valid_text("a" * 51) is True

    def test_counts_chars_without_newlines(self):
        # 50 newlines should not count as valid text
        assert is_valid_text("\n" * 100) is False

    def test_custom_min_chars(self):
        assert is_valid_text("hello", min_chars=3) is True
        assert is_valid_text("hi", min_chars=3) is False


class TestCleanPdfText:
    def test_removes_extra_newlines(self):
        text = "line1\n\n\n\n\nline2"
        result = clean_pdf_text(text)
        assert "\n\n\n" not in result

    def test_strips_whitespace(self):
        result = clean_pdf_text("   hello   ")
        assert result == "hello"

    def test_preserves_normal_text(self):
        text = "Python developer with 5 years of experience."
        assert clean_pdf_text(text) == text

    def test_preserves_accented_characters(self):
        text = "Développeur expérimenté"
        result = clean_pdf_text(text)
        assert "é" in result


class TestReadUploadedFile:
    def _make_file(self, content: bytes) -> io.BytesIO:
        return io.BytesIO(content)

    def test_reads_utf8_text_file(self):
        content = b"Hello, I am a software engineer."
        file = self._make_file(content)
        # Patch filetype.guess to return None (text/plain fallback)
        with patch("skill_match.utils.filetype.guess", return_value=None):
            result = read_uploaded_file(file)
        assert result == "Hello, I am a software engineer."

    def test_reads_windows_1252_encoding(self):
        content = "Développeur".encode("windows-1252")
        file = self._make_file(content)
        with patch("skill_match.utils.filetype.guess", return_value=None):
            result = read_uploaded_file(file)
        assert "veloppeur" in result  # accent may differ by encoding fallback

    def test_raises_on_unsupported_file_type(self):
        mock_kind = MagicMock()
        mock_kind.mime = "image/png"
        file = self._make_file(b"\x89PNG\r\n")
        with patch("skill_match.utils.filetype.guess", return_value=mock_kind):
            with pytest.raises(ValueError, match="Unsupported file type"):
                read_uploaded_file(file)

    def test_reads_pdf_file(self, tmp_path):
        # Create a minimal real PDF with PyMuPDF
        try:
            import fitz
            pdf_path = tmp_path / "test.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 100), "Python developer with experience in machine learning.")
            doc.save(str(pdf_path))
            doc.close()

            with open(pdf_path, "rb") as f:
                raw = f.read()

            mock_kind = MagicMock()
            mock_kind.mime = "application/pdf"
            file = io.BytesIO(raw)

            with patch("skill_match.utils.filetype.guess", return_value=mock_kind):
                result = read_uploaded_file(file)

            assert isinstance(result, str)
            assert len(result) > 0
        except ImportError:
            pytest.skip("PyMuPDF not available")


class TestExtractPdfText:
    def test_extracts_text_from_digital_pdf(self, tmp_path):
        try:
            import fitz
            pdf_path = tmp_path / "digital.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 100), "Experienced Python developer skilled in machine learning and data science.")
            doc.save(str(pdf_path))
            doc.close()

            result = extract_pdf_text(str(pdf_path))
            assert "Python" in result
        except ImportError:
            pytest.skip("PyMuPDF not available")

    def test_returns_string(self, tmp_path):
        try:
            import fitz
            pdf_path = tmp_path / "test.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 100), "Software engineer resume with skills in Python and Docker.")
            doc.save(str(pdf_path))
            doc.close()

            result = extract_pdf_text(str(pdf_path))
            assert isinstance(result, str)
        except ImportError:
            pytest.skip("PyMuPDF not available")

