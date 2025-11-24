# Quick Start Guide - Personal Finance API

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone or Download the Project

```bash
cd e:\sources\python\selFin
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

For development (includes testing tools):
```bash
pip install -r requirements-dev.txt
```

### 5. Configure Environment

Copy the example environment file:
```bash
copy .env.example .env
```

Edit `.env` and update the database connection:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/finance_db
SECRET_KEY=your-super-secret-key-min-32-characters-long
```

### 6. Create Database

**Option A - Using psql:**
```bash
psql -U postgres
CREATE DATABASE finance_db;
\q
```

**Option B - Using pgAdmin:**
- Right-click on "Databases" → Create → Database
- Name: `finance_db`

### 7. Run Database Migrations

```bash
alembic upgrade head
```

This will create all necessary tables.

### 8. Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

## Testing the API

### Using Swagger UI (Recommended)

1. Open your browser and go to: `http://localhost:8000/docs`
2. You'll see the interactive API documentation
3. Try the following flow:

#### Step 1: Register a User
- Click on `POST /api/v1/auth/register`
- Click "Try it out"
- Enter:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```
- Click "Execute"

#### Step 2: Login
- Click on `POST /api/v1/auth/login`
- Enter the same email and password
- Copy the `access_token` from the response

#### Step 3: Authorize
- Click the "Authorize" button at the top right
- Enter: `Bearer YOUR_ACCESS_TOKEN`
- Click "Authorize"

#### Step 4: Create a Transaction
- Click on `POST /api/v1/transactions`
- Enter:
```json
{
  "type": "EXPENSE",
  "amount": 50000,
  "currency": "VND",
  "date": "2024-11-24T10:00:00",
  "description": "Lunch"
}
```

### Using curl

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"password123\",\"full_name\":\"John Doe\"}"

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@example.com\",\"password\":\"password123\"}"

# Use the token from login response
TOKEN="your-token-here"

# Get transactions
curl -X GET http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN"
```

## Running Tests

```bash
pytest
```

With coverage report:
```bash
pytest --cov=app tests/
```

## Common Issues

### Port Already in Use
If port 8000 is busy, use a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database `finance_db` exists

### Import Errors
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Migration Errors
```bash
# Reset migrations (WARNING: This drops all tables!)
alembic downgrade base
alembic upgrade head
```

## Next Steps

1. **Create Categories** - Use `POST /api/v1/categories` to organize transactions
2. **Create Wallets** - Use `POST /api/v1/wallets` to manage multiple accounts
3. **Set Budgets** - Use `POST /api/v1/budgets` to track spending limits
4. **Add Recurring Transactions** - Automate regular expenses/income
5. **View Analytics** - Use `/api/v1/analytics/*` endpoints for insights

## Development Commands

### Create New Alembic Migration
```bash
alembic revision --autogenerate -m "description of changes"
```

### Apply Migration
```bash
alembic upgrade head
```

### Rollback Last Migration
```bash
alembic downgrade -1
```

### Run in Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- OpenAPI YAML: `openapi/finance-api.yaml`

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the OpenAPI specification in `openapi/finance-api.yaml`
3. Check test files in `tests/` for usage examples

## Project Structure Quick Reference

```
app/
  ├── api/v1/routers/    # API endpoints
  ├── core/              # Config & security
  ├── db/                # Database setup
  ├── models/            # SQLAlchemy models
  ├── schemas/           # Pydantic schemas
  ├── services/          # Business logic
  ├── repositories/      # Database operations
  └── main.py           # App entry point
```
