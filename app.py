from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

import MySQLdb.cursors
from flask import Flask, jsonify, request, session
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
Config.validate()
mysql = MySQL(app)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Authentication required"}), 401
        return view(*args, **kwargs)

    return wrapped


def parse_positive_amount(value):
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Amount must be a valid number")
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Amount must be greater than zero")
    return amount


def parse_iso_date(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValueError("Date must use YYYY-MM-DD format")


@app.get("/health")
def health():
    return jsonify({"success": True, "service": "personal-finance-manager"})


@app.post("/api/auth/register")
def register():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))

    if not 3 <= len(username) <= 100:
        return jsonify({"success": False, "message": "Username must contain 3-100 characters"}), 400
    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must contain at least 8 characters"}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, generate_password_hash(password)),
        )
        mysql.connection.commit()
    except MySQLdb.IntegrityError:
        mysql.connection.rollback()
        return jsonify({"success": False, "message": "Username already exists"}), 409
    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Registration failed")
        return jsonify({"success": False, "message": "Unable to create account"}), 500
    finally:
        cursor.close()

    return jsonify({"success": True, "message": "Account created"}), 201


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", ""))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"success": True, "user": {"id": user["id"], "username": user["username"]}})


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out"})


@app.get("/api/expenses")
@login_required
def list_expenses():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        """SELECT id, category, description, amount, date
           FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC""",
        (session["user_id"],),
    )
    expenses = cursor.fetchall()
    cursor.close()
    return jsonify({"success": True, "data": expenses})


@app.post("/api/expenses")
@login_required
def create_expense():
    payload = request.get_json(silent=True) or {}
    category = str(payload.get("category", "")).strip()
    description = str(payload.get("description", "")).strip()

    if not category or len(category) > 50 or not description or len(description) > 255:
        return jsonify({"success": False, "message": "Invalid category or description"}), 400

    try:
        amount = parse_positive_amount(payload.get("amount"))
        expense_date = parse_iso_date(payload.get("date"))
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            """INSERT INTO expenses (user_id, category, description, amount, date)
               VALUES (%s, %s, %s, %s, %s)""",
            (session["user_id"], category, description, amount, expense_date),
        )
        mysql.connection.commit()
        expense_id = cursor.lastrowid
    except Exception:
        mysql.connection.rollback()
        app.logger.exception("Expense creation failed")
        return jsonify({"success": False, "message": "Unable to create expense"}), 500
    finally:
        cursor.close()

    return jsonify({"success": True, "data": {"id": expense_id}}), 201


@app.get("/api/summary")
@login_required
def summary():
    month = request.args.get("month")
    if not month or len(month) != 7:
        return jsonify({"success": False, "message": "month must use YYYY-MM format"}), 400

    try:
        month_start = date.fromisoformat(f"{month}-01")
    except ValueError:
        return jsonify({"success": False, "message": "Invalid month"}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        """SELECT
             COALESCE((SELECT SUM(amount) FROM income
               WHERE user_id = %s AND date >= %s AND date < DATE_ADD(%s, INTERVAL 1 MONTH)), 0) AS income,
             COALESCE((SELECT SUM(amount) FROM expenses
               WHERE user_id = %s AND date >= %s AND date < DATE_ADD(%s, INTERVAL 1 MONTH)), 0) AS expenses""",
        (session["user_id"], month_start, month_start, session["user_id"], month_start, month_start),
    )
    result = cursor.fetchone()
    cursor.close()
    result["savings"] = result["income"] - result["expenses"]
    return jsonify({"success": True, "month": month, "data": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
