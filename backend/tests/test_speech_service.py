"""Unit tests for the speech assessment service (mock mode)."""

import pytest

from app.services.speech_service import PronunciationResult, SpeechAssessmentService


class TestPronunciationResult:
    """Test suite for PronunciationResult data class."""

    def test_overall_score_calculation(self):
        result = PronunciationResult(
            accuracy=80.0,
            prosody=4.0,  # 4.0 * 20 = 80
            fluency=80.0,
            completeness=80.0,
            recognized_text="hello",
            word_scores={},
        )
        # (80 + 80 + 80 + 80) / 4 = 80
        assert result.overall_score == 80.0

    def test_attributes(self):
        result = PronunciationResult(
            accuracy=90.0,
            prosody=4.5,
            fluency=85.0,
            completeness=95.0,
            recognized_text="test text",
            word_scores={"test": {"accuracy": 90.0}},
        )
        assert result.accuracy_score == 90.0
        assert result.prosody_score == 4.5
        assert result.fluency_score == 85.0
        assert result.completeness_score == 95.0
        assert result.recognized_text == "test text"
        assert result.word_level_scores == {"test": {"accuracy": 90.0}}


class TestSpeechAssessmentServiceMock:
    """Test suite for mock speech assessment."""

    @pytest.mark.asyncio
    async def test_mock_assessment_returns_result(self):
        service = SpeechAssessmentService()
        result = await service.assess_pronunciation(b"audio", "Hello world")
        assert isinstance(result, PronunciationResult)

    @pytest.mark.asyncio
    async def test_mock_assessment_scores_in_range(self):
        service = SpeechAssessmentService()
        result = await service.assess_pronunciation(b"audio", "Test phrase here")
        assert 75 <= result.accuracy_score <= 95
        assert 3.5 <= result.prosody_score <= 5.0
        assert 70 <= result.fluency_score <= 90
        assert 80 <= result.completeness_score <= 100
        assert result.overall_score > 0

    @pytest.mark.asyncio
    async def test_mock_assessment_recognized_text(self):
        service = SpeechAssessmentService()
        reference = "The quick brown fox"
        result = await service.assess_pronunciation(b"audio", reference)
        assert result.recognized_text == reference

    @pytest.mark.asyncio
    async def test_mock_assessment_word_scores(self):
        service = SpeechAssessmentService()
        reference = "Hello world today"
        result = await service.assess_pronunciation(b"audio", reference)
        assert "Hello" in result.word_level_scores
        assert "world" in result.word_level_scores
        assert "today" in result.word_level_scores

    @pytest.mark.asyncio
    async def test_mock_assessment_word_score_structure(self):
        service = SpeechAssessmentService()
        result = await service.assess_pronunciation(b"audio", "Hello")
        word_score = result.word_level_scores["Hello"]
        assert "accuracy" in word_score
        assert "error_type" in word_score
        assert 70 <= word_score["accuracy"] <= 100
        assert word_score["error_type"] in ["None", "Mispronunciation", "Omission"]

    @pytest.mark.asyncio
    async def test_mock_assessment_single_word(self):
        service = SpeechAssessmentService()
        result = await service.assess_pronunciation(b"audio", "Hello")
        assert len(result.word_level_scores) == 1

    @pytest.mark.asyncio
    async def test_mock_assessment_long_phrase(self):
        service = SpeechAssessmentService()
        phrase = "Can you describe your experience with cloud computing platforms"
        result = await service.assess_pronunciation(b"audio", phrase)
        assert len(result.word_level_scores) == len(phrase.split())
