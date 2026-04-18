import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from skill_match.predict import (
    normalize_skill,
    stem_skill,
    extract_skills,
    compare_skills,
    predict,
)

def make_ner_entity(word: str, entity_group: str, score: float = 0.95) -> dict:
    return {"word": word, "entity_group": entity_group, "score": score}


def mock_ner_pipe(entities_by_chunk: list[list[dict]]):
    """Returns a callable that yields a different entity list per call."""
    calls = iter(entities_by_chunk)
    return lambda text: next(calls, [])


class TestNormalizeSkill:
    def test_lowercases_input(self):
        result = normalize_skill("Python")
        assert result == result.lower()

    def test_removes_stopwords(self):
        result = normalize_skill("knowledge of Python")
        assert "of" not in result.split()

    def test_lemmatizes(self):
        result = normalize_skill("managing")
        assert result == "manage"

    def test_handles_all_stopwords_with_fallback(self):
        result = normalize_skill("the")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_strips_whitespace(self):
        assert normalize_skill("  python  ") == normalize_skill("python")


class TestStemSkill:
    def test_morphological_variants_produce_same_stem(self):
        assert stem_skill("managing") == stem_skill("management")

    def test_lowercases_input(self):
        assert stem_skill("Python") == stem_skill("python")

    def test_multi_word_skill(self):
        result = stem_skill("machine learning")
        assert isinstance(result, str)
        assert " " in result

class TestExtractSkills:
    def _make_tokenizer(self):
        tok = MagicMock()
        tok.tokenize = lambda text: text.split()
        return tok

    def test_extracts_skill_entities(self):
        ner = mock_ner_pipe([[make_ner_entity("Python", "SKILL")]])
        result = extract_skills("Python developer", ner, self._make_tokenizer())
        assert any("python" in k for k in result.keys())

    def test_extracts_soft_skill_entities(self):
        ner = mock_ner_pipe([[make_ner_entity("leadership", "SOFT_SKILL")]])
        result = extract_skills("leadership experience", ner, self._make_tokenizer())
        assert len(result) > 0

    def test_filters_low_confidence_entities(self):
        ner = mock_ner_pipe([[make_ner_entity("Python", "SKILL", score=0.5)]])
        result = extract_skills("Python developer", ner, self._make_tokenizer(), confidence=0.7)
        assert len(result) == 0

    def test_ignores_unknown_entity_groups(self):
        ner = mock_ner_pipe([[make_ner_entity("Paris", "LOC")]])
        result = extract_skills("Based in Paris", ner, self._make_tokenizer())
        assert len(result) == 0

    def test_deduplicates_same_skill(self):
        entities = [
            make_ner_entity("Python", "SKILL"),
            make_ner_entity("python", "SKILL"),
        ]
        ner = mock_ner_pipe([entities])
        result = extract_skills("Python python", ner, self._make_tokenizer())
        assert len(result) == 1

    def test_returns_dict(self):
        ner = mock_ner_pipe([[]])
        result = extract_skills("some text", ner, self._make_tokenizer())
        assert isinstance(result, dict)

class TestCompareSkills:
    def test_missing_skill_appears_in_missing(self):
        cv = {"python": "Python"}
        jd = {"docker": "Docker"}
        model = MagicMock()

        model.encode = lambda texts: np.zeros((len(texts), 5))
        result = compare_skills(cv, jd, model, semantic_threshold=0.75)
        assert "Docker" in result["missing"]

    def test_semantic_match_above_threshold(self):
        cv = {"containerisation": "containerisation"}
        jd = {"docker": "Docker"}
        model = MagicMock()
        # Unit vectors — cosine similarity will be 1.0, above any threshold
        model.encode = lambda texts: np.ones((len(texts), 5))
        result = compare_skills(cv, jd, model, semantic_threshold=0.75)
        assert len(result["semantic_matches"]) > 0
        assert result["semantic_matches"][0]["jd_skill"] == "Docker"

    def test_result_has_all_expected_keys(self):
        model = MagicMock()
        model.encode = lambda texts: np.zeros((len(texts), 5))
        result = compare_skills({}, {}, model)
        assert set(result.keys()) == {"cv_skills", "jd_skills", "present", "semantic_matches", "missing"}

    def test_empty_inputs_return_empty_lists(self):
        model = MagicMock()
        model.encode = lambda texts: np.zeros((len(texts), 5))
        result = compare_skills({}, {}, model)
        assert result["present"] == []
        assert result["missing"] == []
        assert result["semantic_matches"] == []


class TestPredict:
    def test_raises_on_empty_cv(self):
        with pytest.raises(ValueError, match="cv_text"):
            predict("", "some job description text here")

    def test_raises_on_empty_jd(self):
        with pytest.raises(ValueError, match="jd_text"):
            predict("some cv text here", "")

    def test_raises_on_non_string_cv(self):
        with pytest.raises(ValueError):
            predict(None, "some job description text here")

    def test_raises_on_non_string_jd(self):
        with pytest.raises(ValueError):
            predict("some cv text here", 123)

    def test_returns_expected_keys(self):
        mock_ner = MagicMock()
        mock_ner.return_value = []
        mock_ner.tokenizer = MagicMock()
        mock_ner.tokenizer.tokenize = lambda t: t.split()

        mock_embedder = MagicMock()
        mock_embedder.encode = lambda texts: np.zeros((len(texts), 5))

        with patch("skill_match.predict._get_models", return_value=(mock_ner, mock_embedder)):
            result = predict("I know Python and Docker", "Looking for Python developer")

        expected_keys = {"cv_skills", "jd_skills", "present", "missing", "semantic_matches", "similarity_score"}
        assert set(result.keys()) == expected_keys

    def test_similarity_score_is_between_0_and_100(self):
        mock_ner = MagicMock()
        mock_ner.return_value = []
        mock_ner.tokenizer = MagicMock()
        mock_ner.tokenizer.tokenize = lambda t: t.split()

        mock_embedder = MagicMock()
        mock_embedder.encode = lambda texts: np.ones((len(texts), 5))

        with patch("skill_match.predict._get_models", return_value=(mock_ner, mock_embedder)):
            result = predict("cv text here with some words", "jd text here with some words")

        assert 0 <= result["similarity_score"] <= 100
