"""Tests for the assessment endpoint."""

import io

import pytest


class TestSubmitAssessment:
    """Test suite for POST /api/v1/assessments/assess."""

    def test_submit_assessment_success(self, client, sample_phrase, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": "test-user-assessment-uuid",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "scores" in data
        assert "recognized_text" in data
        assert data["phrase_id"] == sample_phrase.id

    def test_submit_assessment_returns_scores(self, client, sample_phrase, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": "test-user-scores-uuid",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        data = response.json()
        scores = data["scores"]

        # Mock mode generates scores in these ranges
        assert 0 <= scores["accuracy_score"] <= 100
        assert 0 <= scores["prosody_score"] <= 5
        assert 0 <= scores["fluency_score"] <= 100
        assert 0 <= scores["completeness_score"] <= 100
        assert 0 <= scores["overall_score"] <= 100

    def test_submit_assessment_creates_user(self, client, sample_phrase, wav_audio_bytes, db):
        from app.models.user import User

        user_id = "new-auto-created-user-uuid"
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": user_id,
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 200

        # Verify user was created
        user = db.query(User).filter(User.user_id == user_id).first()
        assert user is not None

    def test_submit_assessment_existing_user(
        self, client, sample_phrase, sample_user, wav_audio_bytes
    ):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": sample_user.user_id,
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == sample_user.id

    def test_submit_assessment_invalid_phrase(self, client, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": "9999",
                "user_id": "test-user-invalid-phrase",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 404

    def test_submit_assessment_missing_audio(self, client, sample_phrase):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": "test-user-no-audio",
            },
        )
        assert response.status_code == 422

    def test_submit_assessment_missing_phrase_id(self, client, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "user_id": "test-user-no-phrase",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 422

    def test_submit_assessment_missing_user_id(self, client, sample_phrase, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert response.status_code == 422

    def test_submit_assessment_word_level_scores(self, client, sample_phrase, wav_audio_bytes):
        response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(sample_phrase.id),
                "user_id": "test-user-word-scores",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        data = response.json()
        assert "word_level_scores" in data
        # Mock mode generates word scores for each word in reference text
        assert isinstance(data["word_level_scores"], dict)

    def test_submit_multiple_assessments_same_phrase(
        self, client, sample_phrase, wav_audio_bytes
    ):
        user_id = "test-user-multiple"

        # Submit twice
        response1 = client.post(
            "/api/v1/assessments/assess",
            data={"phrase_id": str(sample_phrase.id), "user_id": user_id},
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        response2 = client.post(
            "/api/v1/assessments/assess",
            data={"phrase_id": str(sample_phrase.id), "user_id": user_id},
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        # Should be different assessment IDs
        assert response1.json()["id"] != response2.json()["id"]


class TestAssessmentIntegration:
    """Integration tests for the full assessment flow."""

    def test_full_flow_create_dialog_phrase_and_assess(self, client, wav_audio_bytes):
        # 1. Create a dialog
        dialog_response = client.post(
            "/api/v1/dialogs",
            json={
                "title": "Integration Test Dialog",
                "category": "IELTS_Part1",
                "description": "Testing the full flow",
            },
        )
        assert dialog_response.status_code == 201
        dialog_id = dialog_response.json()["id"]

        # 2. Create a phrase
        phrase_response = client.post(
            "/api/v1/phrases",
            json={
                "dialog_id": dialog_id,
                "reference_text": "What is your favorite hobby?",
                "order": 1,
            },
        )
        assert phrase_response.status_code == 201
        phrase_id = phrase_response.json()["id"]

        # 3. Submit assessment
        assess_response = client.post(
            "/api/v1/assessments/assess",
            data={
                "phrase_id": str(phrase_id),
                "user_id": "integration-test-user",
            },
            files={"audio": ("recording.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
        )
        assert assess_response.status_code == 200
        assessment = assess_response.json()
        assert assessment["phrase_id"] == phrase_id
        assert assessment["scores"]["overall_score"] > 0

        # 4. Check user progress (use integer user ID from assessment response)
        db_user_id = assessment["user_id"]
        progress_response = client.get(f"/api/v1/users/{db_user_id}/progress")
        assert progress_response.status_code == 200
        progress = progress_response.json()
        assert progress["total_assessments"] == 1
        assert progress["average_overall_score"] > 0

        # 5. Check user assessment history
        history_response = client.get(f"/api/v1/users/{db_user_id}/assessments")
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) == 1
        assert history[0]["phrase_text"] == "What is your favorite hobby?"

    def test_flow_multiple_phrases_multiple_assessments(self, client, wav_audio_bytes):
        # Create dialog with multiple phrases
        dialog_resp = client.post(
            "/api/v1/dialogs",
            json={"title": "Multi-phrase Dialog", "category": "Travel"},
        )
        dialog_id = dialog_resp.json()["id"]

        phrases = []
        for i, text in enumerate(["Good morning.", "How are you?", "Thank you."]):
            resp = client.post(
                "/api/v1/phrases",
                json={"dialog_id": dialog_id, "reference_text": text, "order": i},
            )
            phrases.append(resp.json()["id"])

        # Assess each phrase
        user_id = "multi-phrase-user"
        db_user_id = None
        for phrase_id in phrases:
            resp = client.post(
                "/api/v1/assessments/assess",
                data={"phrase_id": str(phrase_id), "user_id": user_id},
                files={"audio": ("r.wav", io.BytesIO(wav_audio_bytes), "audio/wav")},
            )
            assert resp.status_code == 200
            if db_user_id is None:
                db_user_id = resp.json()["user_id"]

        # Check progress (use integer user ID)
        progress = client.get(f"/api/v1/users/{db_user_id}/progress").json()
        assert progress["total_assessments"] == 3
        assert progress["categories_practiced"]["Travel"] == 3
