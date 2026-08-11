from unittest.mock import MagicMock, patch


def test_create_expense_uses_database_and_returns_created(client):
    cursor = MagicMock()
    cursor.lastrowid = 42
    connection = MagicMock()
    connection.cursor.return_value = cursor

    with client.session_transaction() as session:
        session["user_id"] = 7

    with patch("app.mysql.connection", connection):
        response = client.post(
            "/api/expenses",
            json={
                "category": "Food",
                "description": "Lunch",
                "amount": "125.50",
                "date": "2026-08-11",
            },
        )

    assert response.status_code == 201
    assert response.get_json()["data"]["id"] == 42
    cursor.execute.assert_called_once()
    connection.commit.assert_called_once()
