"""
Speech assessment service using Azure Cognitive Services Speech SDK.
Supports both mock mode (for local development) and real Azure mode.
"""
import random
import logging
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

# Azure Speech SDK import (optional, only needed when MOCK_MODE=false)
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SDK_AVAILABLE = True
except ImportError:
    AZURE_SDK_AVAILABLE = False
    logger.warning("Azure Speech SDK not available. Only mock mode will work.")


class PronunciationResult:
    """Container for pronunciation assessment results."""

    def __init__(
        self,
        accuracy: float,
        prosody: float,
        fluency: float,
        completeness: float,
        recognized_text: str,
        word_scores: Dict[str, Any]
    ):
        self.accuracy_score = accuracy
        self.prosody_score = prosody
        self.fluency_score = fluency
        self.completeness_score = completeness
        self.overall_score = (accuracy + (prosody * 20) + fluency + completeness) / 4
        self.recognized_text = recognized_text
        self.word_level_scores = word_scores


class SpeechAssessmentService:
    """
    Service for pronunciation assessment.

    In mock mode: Returns randomized realistic scores.
    In Azure mode: Uses Azure Speech SDK for real assessment.
    """

    def __init__(self):
        self.mock_mode = settings.MOCK_MODE

        if not self.mock_mode and not AZURE_SDK_AVAILABLE:
            raise RuntimeError(
                "Azure Speech SDK is not available. Install with: pip install azure-cognitiveservices-speech"
            )

    async def assess_pronunciation(
        self,
        audio_bytes: bytes,
        reference_text: str
    ) -> PronunciationResult:
        """
        Assess pronunciation from audio bytes.

        Args:
            audio_bytes: Audio file content (WAV format)
            reference_text: Expected text to be spoken

        Returns:
            PronunciationResult with scores and detailed feedback

        Raises:
            Exception: If assessment fails
        """
        if self.mock_mode:
            logger.info("Using mock pronunciation assessment")
            return self._mock_assessment(reference_text)

        logger.info("Using Azure Speech SDK for pronunciation assessment")
        return await self._azure_assessment(audio_bytes, reference_text)

    def _mock_assessment(self, reference_text: str) -> PronunciationResult:
        """
        Generate mock assessment scores for local development.
        Returns realistic randomized scores.
        """
        words = reference_text.split()
        word_scores = {}

        for word in words:
            # Randomize accuracy for each word (70-100%)
            accuracy = random.uniform(70, 100)
            error_type = random.choice([
                "None",
                "None",
                "None",  # Most words correct
                "Mispronunciation",
                "Omission"
            ])

            word_scores[word] = {
                "accuracy": round(accuracy, 1),
                "error_type": error_type
            }

        # Generate overall scores with some variation
        accuracy = random.uniform(75, 95)
        prosody = random.uniform(3.5, 5.0)
        fluency = random.uniform(70, 90)
        completeness = random.uniform(80, 100)

        return PronunciationResult(
            accuracy=accuracy,
            prosody=prosody,
            fluency=fluency,
            completeness=completeness,
            recognized_text=reference_text,  # Mock: return same text
            word_scores=word_scores
        )

    async def _azure_assessment(
        self,
        audio_bytes: bytes,
        reference_text: str
    ) -> PronunciationResult:
        """
        Perform real pronunciation assessment using Azure Speech SDK.

        Uses IELTS-like grading system with phoneme-level granularity.
        """
        try:
            # Configure Speech SDK
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.SPEECH_KEY,
                region=settings.SPEECH_REGION
            )

            # Configure pronunciation assessment
            pron_config = speechsdk.PronunciationAssessmentConfig(
                reference_text=reference_text,
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
                enable_miscue=True
            )

            # Enable prosody assessment
            pron_config.enable_prosody_assessment()

            # Create audio stream from bytes
            stream = speechsdk.audio.PushAudioInputStream()
            stream.write(audio_bytes)
            stream.close()

            audio_config = speechsdk.audio.AudioConfig(stream=stream)

            # Create recognizer and apply pronunciation config
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            pron_config.apply_to(recognizer)

            # Perform recognition
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                # Extract pronunciation assessment results
                pron_result = speechsdk.PronunciationAssessmentResult(result)

                # Extract word-level scores
                word_scores = self._extract_word_scores(result)

                return PronunciationResult(
                    accuracy=pron_result.accuracy_score,
                    prosody=pron_result.prosody_score / 20,  # Convert 0-100 to 0-5
                    fluency=pron_result.fluency_score,
                    completeness=pron_result.completeness_score,
                    recognized_text=result.text,
                    word_scores=word_scores
                )
            elif result.reason == speechsdk.ResultReason.NoMatch:
                raise Exception("No speech could be recognized from the audio")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = speechsdk.CancellationDetails(result)
                raise Exception(f"Speech recognition canceled: {cancellation.reason}")
            else:
                raise Exception(f"Unexpected result reason: {result.reason}")

        except Exception as e:
            logger.error(f"Azure speech assessment failed: {str(e)}")
            raise Exception(f"Speech assessment failed: {str(e)}")

    def _extract_word_scores(self, result: Any) -> Dict[str, Any]:
        """
        Extract word-level scores from Azure Speech SDK result.

        Returns dictionary mapping words to their accuracy and error type.
        """
        word_scores = {}

        try:
            # Parse JSON result for detailed word scores
            import json
            result_json = json.loads(result.properties.get(
                speechsdk.PropertyId.SpeechServiceResponse_JsonResult
            ))

            if "NBest" in result_json and len(result_json["NBest"]) > 0:
                words = result_json["NBest"][0].get("Words", [])

                for word_info in words:
                    word = word_info.get("Word", "")
                    accuracy = word_info.get("PronunciationAssessment", {}).get("AccuracyScore", 0)
                    error_type = word_info.get("PronunciationAssessment", {}).get("ErrorType", "None")

                    word_scores[word] = {
                        "accuracy": accuracy,
                        "error_type": error_type
                    }
        except Exception as e:
            logger.warning(f"Could not extract word-level scores: {str(e)}")

        return word_scores
