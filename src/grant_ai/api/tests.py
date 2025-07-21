"""Automated API tests for Grant Research AI."""

import requests


def test_health_endpoint():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# TODO: Add tests for grant, organization, and application endpoints
