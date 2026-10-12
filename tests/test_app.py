from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ACTIVITY_NAME = "Chess Club"
ACTIVITY_PATH = quote(ACTIVITY_NAME, safe="")
STUDENT_EMAIL = "student@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            ACTIVITY_NAME: {
                "name": ACTIVITY_NAME,
                "description": "Practice chess",
                "schedule": "Fridays at 3:30 PM",
                "max_participants": 12,
                "participants": [],
                "category": "Intellectual",
            }
        },
    )
    return TestClient(app_module.app)


def test_root_redirects_to_activity_page(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_current_activities(client):
    # Arrange
    expected_activity = app_module.activities[ACTIVITY_NAME]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    signup_url = f"/activities/{ACTIVITY_PATH}/signup"

    # Act
    response = client.post(signup_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {STUDENT_EMAIL} for {ACTIVITY_NAME}"
    }
    assert STUDENT_EMAIL in app_module.activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    app_module.activities[ACTIVITY_NAME]["participants"].append(STUDENT_EMAIL)
    signup_url = f"/activities/{ACTIVITY_PATH}/signup"

    # Act
    response = client.post(signup_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [STUDENT_EMAIL]


def test_signup_rejects_unknown_activity(client):
    # Arrange
    signup_url = "/activities/Unknown%20Activity/signup"

    # Act
    response = client.post(signup_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    another_student = "another@mergington.edu"
    app_module.activities[ACTIVITY_NAME]["participants"] = [
        STUDENT_EMAIL,
        another_student,
    ]
    unregister_url = f"/activities/{ACTIVITY_PATH}/participants"

    # Act
    response = client.delete(unregister_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {STUDENT_EMAIL} from {ACTIVITY_NAME}"
    }
    assert app_module.activities[ACTIVITY_NAME]["participants"] == [another_student]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    unregister_url = "/activities/Unknown%20Activity/participants"

    # Act
    response = client.delete(unregister_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    unregister_url = f"/activities/{ACTIVITY_PATH}/participants"

    # Act
    response = client.delete(unregister_url, params={"email": STUDENT_EMAIL})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
