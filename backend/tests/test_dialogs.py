"""Tests for the dialogs CRUD endpoints."""

import pytest


class TestListDialogs:
    """Test suite for GET /api/v1/dialogs."""

    def test_list_dialogs_empty(self, client):
        response = client.get("/api/v1/dialogs")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_dialogs_returns_all(self, client, create_dialog):
        create_dialog(title="Dialog 1", category="Travel")
        create_dialog(title="Dialog 2", category="IELTS_Part1")

        response = client.get("/api/v1/dialogs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_dialogs_filter_by_category(self, client, create_dialog):
        create_dialog(title="Travel Dialog", category="Travel")
        create_dialog(title="IELTS Dialog", category="IELTS_Part1")

        response = client.get("/api/v1/dialogs?category=Travel")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "Travel"

    def test_list_dialogs_filter_nonexistent_category(self, client, create_dialog):
        create_dialog(title="Travel Dialog", category="Travel")

        response = client.get("/api/v1/dialogs?category=NonExistent")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_dialogs_includes_phrases(self, client, create_dialog, create_phrase):
        dialog = create_dialog(title="Dialog with phrases")
        create_phrase(dialog_id=dialog.id, reference_text="Phrase 1")
        create_phrase(dialog_id=dialog.id, reference_text="Phrase 2")

        response = client.get("/api/v1/dialogs")
        data = response.json()
        assert len(data) == 1
        assert len(data[0]["phrases"]) == 2


class TestGetDialog:
    """Test suite for GET /api/v1/dialogs/{dialog_id}."""

    def test_get_dialog_by_id(self, client, sample_dialog):
        response = client.get(f"/api/v1/dialogs/{sample_dialog.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_dialog.id
        assert data["title"] == "Test Dialog"
        assert data["category"] == "IELTS_Part1"

    def test_get_dialog_includes_phrases(self, client, create_dialog, create_phrase):
        dialog = create_dialog()
        create_phrase(dialog_id=dialog.id, reference_text="First phrase")
        create_phrase(dialog_id=dialog.id, reference_text="Second phrase")

        response = client.get(f"/api/v1/dialogs/{dialog.id}")
        data = response.json()
        assert len(data["phrases"]) == 2

    def test_get_dialog_not_found(self, client):
        response = client.get("/api/v1/dialogs/9999")
        assert response.status_code == 404


class TestCreateDialog:
    """Test suite for POST /api/v1/dialogs."""

    def test_create_dialog(self, client):
        payload = {
            "title": "New Dialog",
            "category": "Professional",
            "description": "A professional dialog",
            "difficulty_level": "Advanced",
        }
        response = client.post("/api/v1/dialogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Dialog"
        assert data["category"] == "Professional"
        assert data["description"] == "A professional dialog"
        assert data["difficulty_level"] == "Advanced"
        assert "id" in data
        assert "created_at" in data

    def test_create_dialog_minimal(self, client):
        payload = {
            "title": "Minimal Dialog",
            "category": "General",
        }
        response = client.post("/api/v1/dialogs", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["difficulty_level"] == "Intermediate"  # default
        assert data["description"] is None

    def test_create_dialog_missing_title(self, client):
        payload = {"category": "General"}
        response = client.post("/api/v1/dialogs", json=payload)
        assert response.status_code == 422

    def test_create_dialog_missing_category(self, client):
        payload = {"title": "No Category"}
        response = client.post("/api/v1/dialogs", json=payload)
        assert response.status_code == 422


class TestUpdateDialog:
    """Test suite for PUT /api/v1/dialogs/{dialog_id}."""

    def test_update_dialog_title(self, client, sample_dialog):
        payload = {"title": "Updated Title"}
        response = client.put(f"/api/v1/dialogs/{sample_dialog.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["category"] == "IELTS_Part1"  # unchanged

    def test_update_dialog_category(self, client, sample_dialog):
        payload = {"category": "Travel"}
        response = client.put(f"/api/v1/dialogs/{sample_dialog.id}", json=payload)
        assert response.status_code == 200
        assert response.json()["category"] == "Travel"

    def test_update_dialog_all_fields(self, client, sample_dialog):
        payload = {
            "title": "Fully Updated",
            "category": "Professional",
            "description": "Updated description",
            "difficulty_level": "Advanced",
        }
        response = client.put(f"/api/v1/dialogs/{sample_dialog.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Fully Updated"
        assert data["category"] == "Professional"
        assert data["description"] == "Updated description"
        assert data["difficulty_level"] == "Advanced"

    def test_update_dialog_not_found(self, client):
        payload = {"title": "Ghost"}
        response = client.put("/api/v1/dialogs/9999", json=payload)
        assert response.status_code == 404


class TestDeleteDialog:
    """Test suite for DELETE /api/v1/dialogs/{dialog_id}."""

    def test_delete_dialog(self, client, sample_dialog):
        response = client.delete(f"/api/v1/dialogs/{sample_dialog.id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/v1/dialogs/{sample_dialog.id}")
        assert response.status_code == 404

    def test_delete_dialog_cascades_phrases(self, client, create_dialog, create_phrase):
        dialog = create_dialog()
        phrase = create_phrase(dialog_id=dialog.id)

        response = client.delete(f"/api/v1/dialogs/{dialog.id}")
        assert response.status_code == 204

        # Phrase should also be gone
        response = client.get(f"/api/v1/phrases/{phrase.id}")
        assert response.status_code == 404

    def test_delete_dialog_not_found(self, client):
        response = client.delete("/api/v1/dialogs/9999")
        assert response.status_code == 404
