def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_login_page_is_available(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_register_page_is_available(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Create your account" in response.data


def test_dashboard_redirects_unauthenticated_user(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_expenses_api_requires_authentication(client):
    response = client.get("/api/expenses")
    assert response.status_code == 401
    assert response.get_json()["message"] == "Authentication required"
