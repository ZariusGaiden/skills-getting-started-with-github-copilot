import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def get_activities(client):
    return client.get("/activities")


def signup(client, activity_name, email):
    return client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )


def remove_participant(client, activity_name, email):
    return client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )


def test_root_redirect(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities(client):
    # Arrange
    expected_activities = {"Chess Club", "Programming Class"}

    # Act
    response = get_activities(client)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert expected_activities.issubset(data.keys())
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]


def test_signup_success(client):
    # Arrange
    test_email = "test_success@example.com"
    activity_name = "Chess%20Club"

    # Act
    response = signup(client, activity_name, test_email)

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]

    # Act
    activities_response = get_activities(client)
    activities = activities_response.json()

    # Assert
    assert test_email in activities["Chess Club"]["participants"]


def test_signup_duplicate(client):
    # Arrange
    test_email = "duplicate@example.com"
    activity_name = "Programming%20Class"

    # Act
    first_response = signup(client, activity_name, test_email)

    # Assert
    assert first_response.status_code == 200

    # Act
    second_response = signup(client, activity_name, test_email)

    # Assert
    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"]


def test_signup_invalid_activity(client):
    # Arrange
    test_email = "invalid@example.com"
    activity_name = "NonExistent"

    # Act
    response = signup(client, activity_name, test_email)

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant_success(client):
    # Arrange
    test_email = "remove_success@example.com"
    activity_name = "Gym%20Class"
    signup(client, activity_name, test_email)

    # Act
    response = remove_participant(client, activity_name, test_email)

    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]

    # Act
    activities_response = get_activities(client)
    activities = activities_response.json()

    # Assert
    assert test_email not in activities["Gym Class"]["participants"]


def test_remove_nonexistent_participant(client):
    # Arrange
    activity_name = "Chess%20Club"
    test_email = "nonexistent@example.com"

    # Act
    response = remove_participant(client, activity_name, test_email)

    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_remove_invalid_activity(client):
    # Arrange
    activity_name = "InvalidActivity"
    test_email = "invalid@example.com"

    # Act
    response = remove_participant(client, activity_name, test_email)

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_activity_availability_consistency(client):
    # Act
    response = get_activities(client)
    activities = response.json()

    # Assert
    for details in activities.values():
        assert len(details["participants"]) <= details["max_participants"]
