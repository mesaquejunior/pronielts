"""Tests for the phrases CRUD endpoints."""

import pytest


class TestGetPhrase:
    """Test suite for GET /api/v1/phrases/{phrase_id}."""

    def test_get_phrase_by_id(self, client, sample_phrase):
        response = client.get(f"/api/v1/phrases/{sample_phrase.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_phrase.id
        assert data["reference_text"] == "Hello, how are you today?"
        assert data["difficulty"] == "Intermediate"

    def test_get_phrase_not_found(self, client):
        response = client.get("/api/v1/phrases/9999")
        assert response.status_code == 404


class TestCreatePhrase:
    """Test suite for POST /api/v1/phrases."""

    def test_create_phrase(self, client, sample_dialog):
        payload = {
            "dialog_id": sample_dialog.id,
            "reference_text": "I would like a coffee, please.",
            "order": 1,
            "difficulty": "Beginner",
        }
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["reference_text"] == "I would like a coffee, please."
        assert data["order"] == 1
        assert data["difficulty"] == "Beginner"
        assert data["dialog_id"] == sample_dialog.id

    def test_create_phrase_with_phonetic(self, client, sample_dialog):
        payload = {
            "dialog_id": sample_dialog.id,
            "reference_text": "Hello",
            "phonetic_transcription": "hɛˈloʊ",
        }
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["phonetic_transcription"] == "hɛˈloʊ"

    def test_create_phrase_minimal(self, client, sample_dialog):
        payload = {
            "dialog_id": sample_dialog.id,
            "reference_text": "Simple phrase.",
        }
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["order"] == 0  # default
        assert data["difficulty"] == "Intermediate"  # default

    def test_create_phrase_invalid_dialog(self, client):
        payload = {
            "dialog_id": 9999,
            "reference_text": "Orphan phrase",
        }
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 404

    def test_create_phrase_missing_text(self, client, sample_dialog):
        payload = {"dialog_id": sample_dialog.id}
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 422

    def test_create_phrase_empty_text(self, client, sample_dialog):
        payload = {
            "dialog_id": sample_dialog.id,
            "reference_text": "",
        }
        response = client.post("/api/v1/phrases", json=payload)
        assert response.status_code == 422


class TestUpdatePhrase:
    """Test suite for PUT /api/v1/phrases/{phrase_id}."""

    def test_update_phrase_text(self, client, sample_phrase):
        payload = {"reference_text": "Updated reference text."}
        response = client.put(f"/api/v1/phrases/{sample_phrase.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["reference_text"] == "Updated reference text."

    def test_update_phrase_order(self, client, sample_phrase):
        payload = {"order": 5}
        response = client.put(f"/api/v1/phrases/{sample_phrase.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["order"] == 5

    def test_update_phrase_difficulty(self, client, sample_phrase):
        payload = {"difficulty": "Advanced"}
        response = client.put(f"/api/v1/phrases/{sample_phrase.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["difficulty"] == "Advanced"

    def test_update_phrase_not_found(self, client):
        payload = {"reference_text": "Ghost phrase"}
        response = client.put("/api/v1/phrases/9999", json=payload)
        assert response.status_code == 404


class TestDeletePhrase:
    """Test suite for DELETE /api/v1/phrases/{phrase_id}."""

    def test_delete_phrase(self, client, sample_phrase):
        response = client.delete(f"/api/v1/phrases/{sample_phrase.id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/v1/phrases/{sample_phrase.id}")
        assert response.status_code == 404

    def test_delete_phrase_not_found(self, client):
        response = client.delete("/api/v1/phrases/9999")
        assert response.status_code == 404
