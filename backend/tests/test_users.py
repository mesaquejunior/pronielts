"""Tests for the users endpoints."""

import pytest


class TestUserAssessments:
    """Test suite for GET /api/v1/users/{user_id}/assessments."""

    def test_get_user_assessments(self, client, sample_assessment, sample_user):
        response = client.get(f"/api/v1/users/{sample_user.id}/assessments")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["overall_score"] == 85.0

    def test_get_user_assessments_empty(self, client, sample_user):
        response = client.get(f"/api/v1/users/{sample_user.id}/assessments")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_user_assessments_multiple(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        phrase1 = create_phrase(dialog_id=sample_dialog.id, reference_text="Phrase 1")
        phrase2 = create_phrase(dialog_id=sample_dialog.id, reference_text="Phrase 2")
        create_assessment(user_id=sample_user.id, phrase_id=phrase1.id, overall_score=80.0)
        create_assessment(user_id=sample_user.id, phrase_id=phrase2.id, overall_score=90.0)

        response = client.get(f"/api/v1/users/{sample_user.id}/assessments")
        data = response.json()
        assert len(data) == 2

    def test_get_user_assessments_with_limit(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        for i in range(5):
            phrase = create_phrase(
                dialog_id=sample_dialog.id, reference_text=f"Phrase {i}", order=i
            )
            create_assessment(user_id=sample_user.id, phrase_id=phrase.id)

        response = client.get(f"/api/v1/users/{sample_user.id}/assessments?limit=3")
        data = response.json()
        assert len(data) == 3

    def test_get_user_assessments_with_offset(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        for i in range(5):
            phrase = create_phrase(
                dialog_id=sample_dialog.id, reference_text=f"Phrase {i}", order=i
            )
            create_assessment(user_id=sample_user.id, phrase_id=phrase.id)

        response = client.get(f"/api/v1/users/{sample_user.id}/assessments?offset=3")
        data = response.json()
        assert len(data) == 2  # 5 total - 3 offset = 2

    def test_get_user_assessments_user_not_found(self, client):
        response = client.get("/api/v1/users/9999/assessments")
        assert response.status_code == 404

    def test_get_user_assessments_includes_phrase_text(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        phrase = create_phrase(
            dialog_id=sample_dialog.id, reference_text="The quick brown fox"
        )
        create_assessment(user_id=sample_user.id, phrase_id=phrase.id)

        response = client.get(f"/api/v1/users/{sample_user.id}/assessments")
        data = response.json()
        assert data[0]["phrase_text"] == "The quick brown fox"


class TestUserProgress:
    """Test suite for GET /api/v1/users/{user_id}/progress."""

    def test_get_user_progress(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        phrase = create_phrase(dialog_id=sample_dialog.id)
        create_assessment(
            user_id=sample_user.id,
            phrase_id=phrase.id,
            accuracy_score=85.0,
            prosody_score=4.0,
            fluency_score=80.0,
            completeness_score=90.0,
            overall_score=85.0,
        )

        response = client.get(f"/api/v1/users/{sample_user.id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["total_assessments"] == 1
        assert data["average_overall_score"] == 85.0
        assert data["average_accuracy"] == 85.0
        assert data["best_score"] == 85.0
        assert data["worst_score"] == 85.0

    def test_get_user_progress_no_assessments(self, client, sample_user):
        response = client.get(f"/api/v1/users/{sample_user.id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["total_assessments"] == 0
        assert data["average_overall_score"] == 0
        assert data["best_score"] == 0
        assert data["worst_score"] == 0

    def test_get_user_progress_multiple_assessments(
        self, client, sample_user, create_assessment, create_phrase, sample_dialog
    ):
        phrase1 = create_phrase(dialog_id=sample_dialog.id, reference_text="P1")
        phrase2 = create_phrase(dialog_id=sample_dialog.id, reference_text="P2")
        create_assessment(user_id=sample_user.id, phrase_id=phrase1.id, overall_score=80.0)
        create_assessment(user_id=sample_user.id, phrase_id=phrase2.id, overall_score=90.0)

        response = client.get(f"/api/v1/users/{sample_user.id}/progress")
        data = response.json()
        assert data["total_assessments"] == 2
        assert data["average_overall_score"] == 85.0
        assert data["best_score"] == 90.0
        assert data["worst_score"] == 80.0

    def test_get_user_progress_categories_practiced(
        self, client, sample_user, create_dialog, create_phrase, create_assessment
    ):
        dialog_travel = create_dialog(title="Travel", category="Travel")
        dialog_ielts = create_dialog(title="IELTS", category="IELTS_Part1")

        phrase_travel = create_phrase(dialog_id=dialog_travel.id, reference_text="Travel phrase")
        phrase_ielts = create_phrase(dialog_id=dialog_ielts.id, reference_text="IELTS phrase")

        create_assessment(user_id=sample_user.id, phrase_id=phrase_travel.id)
        create_assessment(user_id=sample_user.id, phrase_id=phrase_ielts.id)

        response = client.get(f"/api/v1/users/{sample_user.id}/progress")
        data = response.json()
        assert "Travel" in data["categories_practiced"]
        assert "IELTS_Part1" in data["categories_practiced"]

    def test_get_user_progress_user_not_found(self, client):
        response = client.get("/api/v1/users/9999/progress")
        assert response.status_code == 404
