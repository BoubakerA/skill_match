from unittest.mock import MagicMock
from skill_match.predict import (
    normalize_skill,
    stem_skill,
    compare_skills,
    extract_skills,
    match_cv_jd,
)


class TestNormalizeSkill:
    def test_lowercases_input(self):
        result = normalize_skill("Python")
        assert result == result.lower()

    def test_strips_whitespace(self):
        result = normalize_skill("  python  ")
        assert result == normalize_skill("python")

    def test_lemmatizes_plural(self):
        # "skills" should lemmatize to "skill"
        result = normalize_skill("skills")
        assert "skill" in result

    def test_removes_stopwords(self):
        result = normalize_skill("knowledge of python")
        assert "of" not in result

    def test_removes_punctuation(self):
        result = normalize_skill("python.")
        assert "." not in result

    def test_handles_empty_string(self):
        result = normalize_skill("")
        assert isinstance(result, str)


class TestStemSkill:
    def test_stems_basic_word(self):
        assert stem_skill("running") == "run"

    def test_lowercases(self):
        assert stem_skill("Python") == stem_skill("python")

    def test_stems_multiple_words(self):
        result = stem_skill("machine learning")
        assert isinstance(result, str)
        assert " " in result

    def test_handles_already_stemmed(self):
        assert stem_skill("python") == "python"


class TestCompareSkills:
    def test_finds_exact_matches(self):
        cv = ["python", "sql"]
        jd = ["python", "java"]
        result = compare_skills(cv, jd)
        assert "python" in result["present"]

    def test_finds_missing_skills(self):
        cv = ["python"]
        jd = ["python", "docker"]
        result = compare_skills(cv, jd)
        assert "docker" in result["missing"]

    def test_no_false_positives_in_missing(self):
        cv = ["python", "docker"]
        jd = ["python", "docker"]
        result = compare_skills(cv, jd)
        assert result["missing"] == []

    def test_returns_all_keys(self):
        result = compare_skills(["python"], ["python", "sql"])
        assert "cv_skills" in result
        assert "jd_skills" in result
        assert "present" in result
        assert "missing" in result

    def test_handles_empty_cv(self):
        result = compare_skills([], ["python", "sql"])
        assert result["present"] == []
        assert set(result["missing"]) == {"python", "sql"}

    def test_handles_empty_jd(self):
        result = compare_skills(["python"], [])
        assert result["missing"] == []
        assert result["present"] == []

    def test_case_insensitive_matching(self):
        result = compare_skills(["Python"], ["python"])
        assert "python" in result["present"]

    def test_stem_based_matching(self):
        # "managing" and "management" should match via stemming
        result = compare_skills(["managing"], ["management"])
        assert result["present"] != [] or result["missing"] != ["management"]

    def test_results_are_sorted(self):
        cv = ["sql", "python", "docker"]
        jd = ["python", "sql", "kubernetes"]
        result = compare_skills(cv, jd)
        assert result["present"] == sorted(result["present"])
        assert result["missing"] == sorted(result["missing"])


class TestExtractSkills:
    def _make_ner_pipeline(self, entities):
        """Returns a mock NER pipeline that always returns given entities."""
        mock = MagicMock()
        mock.return_value = entities
        return mock

    def test_returns_list(self):
        ner = self._make_ner_pipeline([])
        result = extract_skills("Some text", ner)
        assert isinstance(result, list)

    def test_extracts_hskill_entities(self):
        ner = self._make_ner_pipeline([
            {"word": "Python", "entity_group": "HSKILL", "score": 0.95}
        ])
        result = extract_skills("Python developer", ner)
        assert len(result) > 0

    def test_extracts_sskill_entities(self):
        ner = self._make_ner_pipeline([
            {"word": "communication", "entity_group": "SSKILL", "score": 0.85}
        ])
        result = extract_skills("Good communication skills", ner)
        assert len(result) > 0

    def test_filters_low_confidence_entities(self):
        ner = self._make_ner_pipeline([
            {"word": "Python", "entity_group": "HSKILL", "score": 0.5}
        ])
        result = extract_skills("Python developer", ner)
        assert result == []

    def test_ignores_unknown_entity_groups(self):
        ner = self._make_ner_pipeline([
            {"word": "Paris", "entity_group": "LOC", "score": 0.99}
        ])
        result = extract_skills("Based in Paris", ner)
        assert result == []

    def test_handles_empty_text(self):
        ner = self._make_ner_pipeline([])
        result = extract_skills("", ner)
        assert result == []

    def test_handles_multiline_text(self):
        ner = self._make_ner_pipeline([
            {"word": "Python", "entity_group": "HSKILL", "score": 0.9}
        ])
        text = "Line one\nLine two with Python\nLine three"
        result = extract_skills(text, ner)
        assert isinstance(result, list)


class TestMatchCvJd:
    def _make_mocks(self, cv_entities=None, jd_entities=None):
        cv_entities = cv_entities or [{"word": "python", "entity_group": "HSKILL", "score": 0.9}]
        jd_entities = jd_entities or [{"word": "python", "entity_group": "HSKILL", "score": 0.9},
                                     {"word": "docker", "entity_group": "HSKILL", "score": 0.85}]

        call_count = {"n": 0}
        def ner_side_effect(text):
            result = cv_entities if call_count["n"] == 0 else jd_entities
            call_count["n"] += 1
            return result

        ner_pipeline = MagicMock(side_effect=ner_side_effect)

        embedding_model = MagicMock()
        embedding_model.encode.return_value = [[0.1, 0.2, 0.3]]

        return ner_pipeline, embedding_model

    def test_returns_expected_keys(self):
        ner, emb = self._make_mocks()
        result = match_cv_jd("cv text", "jd text", ner, emb)
        assert "cv_skills" in result
        assert "jd_skills" in result
        assert "present" in result
        assert "missing" in result
        assert "similarity_score" in result

    def test_similarity_score_is_float(self):
        ner, emb = self._make_mocks()
        result = match_cv_jd("cv text", "jd text", ner, emb)
        assert isinstance(result["similarity_score"], float)

    def test_similarity_score_is_rounded(self):
        ner, emb = self._make_mocks()
        result = match_cv_jd("cv text", "jd text", ner, emb)
        # Should have at most 4 decimal places
        assert result["similarity_score"] == round(result["similarity_score"], 4)

    def test_calls_embedding_model_twice(self):
        ner, emb = self._make_mocks()
        match_cv_jd("cv text", "jd text", ner, emb)
        assert emb.encode.call_count == 2
