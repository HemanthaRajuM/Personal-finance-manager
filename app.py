from datetime import date
from functools import wraps

import MySQLdb
import MySQLdb.cursors
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from utils import parse_amount, parse_date

app = Flask(__name__)
app.config.from_object(Config)
Config.validate()
mysql = MySQL(app)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Authentication required"}), 401
            return redirect(url_for("login_page"))
        return view(*args, **kwargs)
    return wrapped


@app.get("/")
@login_required
def dashboard_page():
    return render_template("dashboard.html")


@app.get("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")


@app.get("/register")
def register_page():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("register.html")


@app.get("/health")
def health():
    return jsonify({"success": True, "service": "personal-finance-manager"})


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))
    if not 3 <= len(username) <= 100 or len(password) < 8:
        return jsonify({"success": False, "message": "Use a 3-100 character username and an 8+ character password"}), 400
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, generate_password_hash(password)))
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
    data = request.get_json(silent=True) or {}
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, username, password FROM users WHERE username = %s", (str(data.get("username", "")).strip(),))
    user = cursor.fetchone()
    cursor.close()
    if not user or not check_password_hash(user["password"], str(data.get("password", ""))):
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
    cursor.execute("SELECT id, category, description, amount, date FROM expenses WHERE user_id = %s ORDER BY date DESC, id DESC", (session["user_id"],))
    data = cursor.fetchall()
    cursor.close()
    return jsonify({"success": True, "data": data})


@app.post("/api/expenses")
@login_required
def create_expense():
    data = request.get_json(silent=True) or {}
    category = str(data.get("category", "")).strip()
    description = str(data.get("description", "")).strip()
    if not category or len(category) > 50 or not description or len(description) > 255:
        return jsonify({"success": False, "message": "Invalid category or description"}), 400
    try:
        expense_amount = parse_amount(data.get("amount"))
        expense_date = parse_date(data.get("date"))
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("INSERT INTO expenses (user_id, category, description, amount, date) VALUES (%s, %s, %s, %s, %s)", (session["user_id"], category, description, expense_amount, expense_date))
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
    month = request.args.get("month", "")
    try:
        month_start = date.fromisoformat(f"{month}-01")
    except ValueError:
        return jsonify({"success": False, "message": "month must use YYYY-MM format"}), 400
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COALESCE((SELECT SUM(amount) FROM income WHERE user_id=%s AND date >= %s AND date < DATE_ADD(%s, INTERVAL 1 MONTH)), 0) AS income, COALESCE((SELECT SUM(amount) FROM expenses WHERE user_id=%s AND date >= %s AND date < DATE_ADD(%s, INTERVAL 1 MONTH)), 0) AS expenses", (session["user_id"], month_start, month_start, session["user_id"], month_start, month_start))
    result = cursor.fetchone()
    cursor.close()
    result["savings"] = result["income"] - result["expenses"]
    return jsonify({"success": True, "month": month, "data": result})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
