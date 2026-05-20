def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_new_participant(client):
    response = client.post("/activities/Chess Club/signup?email=tester@mergington.edu")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up tester@mergington.edu for Chess Club"
    }

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert "tester@mergington.edu" in participants


def test_signup_rejects_duplicate_participant(client):
    first_response = client.post(
        "/activities/Chess Club/signup?email=repeat@mergington.edu"
    )
    second_response = client.post(
        "/activities/Chess Club/signup?email=repeat@mergington.edu"
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Student already signed up"}


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup?email=tester@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_existing_participant(client):
    signup_response = client.post(
        "/activities/Chess Club/signup?email=remove-me@mergington.edu"
    )
    unregister_response = client.delete(
        "/activities/Chess Club/unregister?email=remove-me@mergington.edu"
    )

    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert unregister_response.json() == {
        "message": "Unregistered remove-me@mergington.edu from Chess Club"
    }

    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert "remove-me@mergington.edu" not in participants


def test_unregister_rejects_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/unregister?email=missing@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown Club/unregister?email=tester@mergington.edu"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
