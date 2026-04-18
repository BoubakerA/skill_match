import pytest
import io
from unittest.mock import patch, MagicMock
from skill_match.utils import (
    read_uploaded_file,
    clean_pdf_text,
    is_valid_text,
    extract_pdf_text
)

class TestCleanPdfText:
    def test_removes_icon_artifacts(self):
        assert "hello world" in clean_pdf_text("★ hello world ●")

    def test_normalizes_multiple_newlines(self):
        result = clean_pdf_text("line1\n\n\n\nline2")
        assert "\n\n\n" not in result
        assert "line1" in result
        assert "line2" in result

    def test_preserves_regular_characters(self):
        text = "experienced developer"
        result = clean_pdf_text(text)
        assert "experienced" in result
        assert "developer" in result

    def test_strips_surrounding_whitespace(self):
        assert clean_pdf_text("  hello  ").startswith("h")


class TestIsValidText:
    def test_empty_string_is_invalid(self):
        assert not is_valid_text("")

    def test_none_is_invalid(self):
        assert not is_valid_text(None)

    def test_short_text_is_invalid(self):
        assert not is_valid_text("too short")

    def test_long_enough_text_is_valid(self):
        assert is_valid_text("a" * 51)

    def test_exactly_at_threshold_is_invalid(self):
        assert not is_valid_text("a" * 50)

    def test_whitespace_only_is_invalid(self):
        assert not is_valid_text("   \n\n\n   ")

    def test_custom_min_chars(self):
        assert is_valid_text("a" * 11, min_chars=10)
        assert not is_valid_text("a" * 5, min_chars=10)

class TestReadUploadedFile:
    def _make_file(self, content: bytes) -> io.BytesIO:
        return io.BytesIO(content)

    def test_reads_utf8_text_file(self):
        content = b"hello world, this is a plain text file"
        with patch("skill_match.utils.filetype.guess", return_value=None):
            result = read_uploaded_file(self._make_file(content))
        assert result == content.decode("utf-8")

    def test_pdf_delegates_to_extract_pdf_text(self):
        fake_pdf = b"%PDF-1.4 fake pdf content"
        mock_kind = MagicMock()
        mock_kind.mime = "application/pdf"
        with patch("skill_match.utils.filetype.guess", return_value=mock_kind), \
             patch("skill_match.utils.extract_pdf_text", return_value="extracted text") as mock_extract:
            result = read_uploaded_file(self._make_file(fake_pdf))
        assert result == "extracted text"
        mock_extract.assert_called_once()

    def test_temp_file_is_cleaned_up_on_success(self):
        fake_pdf = b"%PDF-1.4 fake"
        mock_kind = MagicMock()
        mock_kind.mime = "application/pdf"
        with patch("skill_match.utils.filetype.guess", return_value=mock_kind), \
             patch("skill_match.utils.extract_pdf_text", return_value="ok"), \
             patch("os.unlink") as mock_unlink:
            read_uploaded_file(self._make_file(fake_pdf))
            assert mock_unlink.called


class TestExtractPdfText:
    def test_uses_pymupdf_when_text_is_valid(self):
        with patch("skill_match.utils.extract_text_pymupdf", return_value="a" * 100), \
             patch("skill_match.utils.extract_text_ocr") as mock_ocr:
            result = extract_pdf_text("fake.pdf")
        assert result == "a" * 100
        mock_ocr.assert_not_called()

    def test_falls_back_to_ocr_when_text_is_too_short(self):
        with patch("skill_match.utils.extract_text_pymupdf", return_value="short"), \
             patch("skill_match.utils.extract_text_ocr", return_value="ocr result") as mock_ocr:
            result = extract_pdf_text("fake.pdf")
        assert result == "ocr result"
        mock_ocr.assert_called_once_with("fake.pdf")

    def test_falls_back_to_ocr_when_pymupdf_returns_empty(self):
        with patch("skill_match.utils.extract_text_pymupdf", return_value=""), \
             patch("skill_match.utils.extract_text_ocr", return_value="ocr fallback"):
            result = extract_pdf_text("fake.pdf")
        assert result == "ocr fallback"
