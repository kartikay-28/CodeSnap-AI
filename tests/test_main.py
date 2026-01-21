"""
Basic tests for the main application
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "CodeSnap AI"}

def test_docs_accessible():
    """Test that API docs are accessible"""
    response = client.get("/docs")
    assert response.status_code == 200