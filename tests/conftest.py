"""
Pytest configuration and shared fixtures for API tests
"""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


# Store initial activities state
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for intramural and league play",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Tennis Club": {
        "description": "Learn tennis skills and play recreational matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 10,
        "participants": []
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and mixed media techniques",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Music Ensemble": {
        "description": "Play instruments and perform in school concerts",
        "schedule": "Mondays and Thursdays, 3:45 PM - 4:45 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Club": {
        "description": "Develop critical thinking and public speaking skills through competitive debate",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Olympiad": {
        "description": "Compete in science and engineering challenges",
        "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 14,
        "participants": []
    }
}


@pytest.fixture
def client():
    """FastAPI TestClient for making HTTP requests to the app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test to ensure test isolation"""
    # Clear existing activities
    activities.clear()
    # Restore initial state with deep copy to prevent mutations
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    # Cleanup after test (restore again)
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
