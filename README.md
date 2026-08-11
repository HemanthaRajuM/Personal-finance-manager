# FinancePro

FinancePro is a multi-user personal finance management platform developed from a fourth-semester DBMS course project and upgraded as a portfolio application.

It allows users to authenticate securely, record expenses, view monthly financial summaries, and analyze personal spending through a responsive dashboard.

## Highlights

- Flask and MySQL application with user-scoped data access.
- Password hashing and secure environment-based configuration.
- Expense API with server-side amount and date validation.
- Monthly income, expense, and savings summaries.
- Responsive dashboard built with Jinja, Bootstrap, CSS, and JavaScript.
- Relational schema with foreign keys, constraints, unique rules, and indexes.
- Pytest unit and route tests.
- GitHub Actions CI workflow for automated testing.

## Architecture

```text
Browser dashboard
       |
       v
Flask routes and JSON API
       |
       v
Validation and authentication layer
       |
       v
MySQL relational database
```

## Database Design

The schema is available in [`database/schema.sql`](database/schema.sql).

Main tables:

- `users` — authentication and account records.
- `income` — income entries belonging to a user.
- `expenses` — categorized expense transactions.
- `budgets` — monthly category-level limits.
- `reminders` — user reminders and completion status.
- `savings_goals` — savings targets and progress.

The schema uses foreign keys with cascading user deletion, positive monetary checks, monthly budget uniqueness, and indexes for user/date/category queries.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health check |
| GET | `/login` | Login page |
| GET | `/register` | Registration page |
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Authenticate a user |
| POST | `/api/auth/logout` | Clear the active session |
| GET | `/api/expenses` | List the logged-in user's expenses |
| POST | `/api/expenses` | Create a validated expense |
| GET | `/api/summary?month=YYYY-MM` | Return monthly income, expenses, and savings |

## Technology Stack

- Python 3.12
- Flask
- MySQL
- Flask-MySQLdb
- Jinja2
- Bootstrap 5
- Pytest
- GitHub Actions

## Project Structure

```text
.
├── app.py
├── config.py
├── utils.py
├── database/
│   └── schema.sql
├── templates/
│   ├── dashboard.html
│   ├── login.html
│   └── register.html
├── static/
│   ├── css/style.css
│   └── js/
├── tests/
│   ├── conftest.py
│   ├── test_api_validation.py
│   ├── test_routes.py
│   └── test_utils.py
├── requirements.txt
└── .env.example
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/HemanthaRajuM/Personal-finance-manager.git
cd Personal-finance-manager
git checkout portfolio-upgrade
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and provide local MySQL credentials:

```env
FLASK_SECRET_KEY=use-a-long-random-value
FLASK_ENV=development
MYSQL_HOST=localhost
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=findb
```

Never commit `.env` or real credentials.

### 5. Create the database

```bash
mysql -u your_mysql_user -p < database/schema.sql
```

### 6. Run the application

```bash
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Testing

Run the complete test suite:

```bash
pytest -q
```

The project also runs tests automatically through GitHub Actions on pushes and pull requests.

## Security Practices

- Passwords are hashed using Werkzeug.
- SQL statements use parameterized values.
- Database records are scoped to the authenticated user.
- Amounts and dates are validated on the server.
- Flask secrets and database credentials are loaded from environment variables.
- Debug mode is disabled in the application entry point.
- Session cookies use HTTP-only and SameSite settings.

This project is an academic and portfolio application. Do not use it with real financial credentials or sensitive production data without a complete security review.

## Known Limitations

- The current demo focuses on expense capture and monthly summaries.
- A production deployment still requires HTTPS, operational monitoring, backups, rate limiting, and a managed secrets solution.
- PDF reports, email notifications, and two-factor authentication are planned features.

## Future Improvements

- Add complete monthly budget CRUD APIs.
- Add income-entry UI and API tests.
- Add database-backed integration tests.
- Add CSV export.
- Add rate limiting and CSRF protection for browser state-changing requests.
- Add deployment configuration and observability.

## Academic Context

Originally developed as a fourth-semester DBMS project. The portfolio branch demonstrates subsequent improvements in secure configuration, relational schema design, API development, automated testing, CI, and documentation.
