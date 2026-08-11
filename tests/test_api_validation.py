import pytest


@pytest.mark.parametrize("amount", ["0", "-1", "not-a-number", None])
def test_expense_rejects_invalid_amount(client, amount):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post("/api/expenses", json={"category": "Food", "description": "Lunch", "amount": amount, "date": "2026-08-11"})
    assert response.status_code == 400
    assert "amount" in response.get_json()["message"].lower()


def test_expense_rejects_invalid_date_before_database_access(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post("/api/expenses", json={"category": "Food", "description": "Lunch", "amount": "100", "date": "11-08-2026"})
    assert response.status_code == 400
    assert "date" in response.get_json()["message"].lower()


def test_expense_rejects_missing_description(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post("/api/expenses", json={"category": "Food", "amount": "100", "date": "2026-08-11"})
    assert response.status_code == 400
    assert "category or description" in response.get_json()["message"].lower()


def test_expense_rejects_overlong_category(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.post("/api/expenses", json={"category": "x" * 51, "description": "Lunch", "amount": "100", "date": "2026-08-11"})
    assert response.status_code == 400
    assert "category or description" in response.get_json()["message"].lower()
