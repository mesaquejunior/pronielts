"""Tests for the health check endpoint."""

import pytest


class TestHealthCheck:
    """Test suite for the /health endpoint."""

    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_contains_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_contains_version(self, client):
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_check_contains_project_name(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["project"] == "PronIELTS API"

    def test_health_check_shows_mock_mode(self, client):
        response = client.get("/health")
        data = response.json()
        assert "mock_mode" in data
        assert data["mock_mode"] is True
