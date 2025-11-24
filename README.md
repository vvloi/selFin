# Personal Finance Management API

A clean-code Python backend for managing personal finances with transactions, budgets, recurring transactions, and analytics.

## Architecture

This project follows a **3-layer architecture**:

- **API Layer** (`app/api/v1/routers/`): FastAPI routers handling HTTP requests/responses
- **Service Layer** (`app/services/`): Business logic and validation
- **Repository Layer** (`app/repositories/`): Database operations (CRUD)

## Tech Stack

- **Python 3.11+**
- **FastAPI** - Web framework
- **SQLAlchemy 2.x** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database
- **JWT** - Authentication
- **Pydantic** - Data validation

## Features

### Authentication & User Management
- User registration with email/password
- JWT-based authentication
- Wallet management

### Transactions
- Create, update, delete transactions (income, expense, transfer)
- Filter by date, category, wallet, type
- Pagination support
- View transactions grouped by day/week/month

### Budgets
- Create budgets by category
- Periodic budgets (monthly, weekly, custom)
- Track spending vs. budget
- Alerts for near-limit and exceeded budgets

### Recurring Transactions
- Create recurring transactions (daily, weekly, monthly, yearly)
- Automatic next run date calculation
- Manual execution support

### Analytics & Reports
- Spending by category (pie chart data)
- Spending trend over time
- Top spending categories
- Export transactions to CSV/PDF

## Project Structure

```
app/
  api/v1/routers/     # API endpoints
  core/               # Configuration and security
  db/                 # Database configuration
  models/             # SQLAlchemy models
  schemas/            # Pydantic schemas
  services/           # Business logic
  repositories/       # Database operations
  main.py             # FastAPI application
alembic/              # Database migrations
openapi/              # OpenAPI specification
tests/                # Tests
```

## Setup & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finance_db
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=False
```

### 3. Setup Database

Create PostgreSQL database:

```bash
createdb finance_db
```

Run migrations:

```bash
alembic upgrade head
```

### 4. Run Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- OpenAPI Spec: `http://localhost:8000/openapi.json`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### Wallets
- `GET /api/v1/wallets` - List wallets
- `POST /api/v1/wallets` - Create wallet
- `GET /api/v1/wallets/{id}` - Get wallet
- `PATCH /api/v1/wallets/{id}` - Update wallet
- `DELETE /api/v1/wallets/{id}` - Delete wallet

### Categories
- `GET /api/v1/categories` - List categories
- `POST /api/v1/categories` - Create category

### Transactions
- `GET /api/v1/transactions` - List transactions (with filters)
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions/{id}` - Get transaction
- `PATCH /api/v1/transactions/{id}` - Update transaction
- `DELETE /api/v1/transactions/{id}` - Delete transaction
- `GET /api/v1/transactions/daily` - Daily grouped transactions
- `GET /api/v1/transactions/weekly` - Weekly grouped transactions
- `GET /api/v1/transactions/monthly` - Monthly grouped transactions

### Budgets
- `GET /api/v1/budgets` - List budgets
- `POST /api/v1/budgets` - Create budget
- `GET /api/v1/budgets/{id}` - Get budget
- `PATCH /api/v1/budgets/{id}` - Update budget
- `DELETE /api/v1/budgets/{id}` - Delete budget
- `GET /api/v1/budgets/summary` - Budget summary

### Recurring Transactions
- `GET /api/v1/recurring-transactions` - List recurring transactions
- `POST /api/v1/recurring-transactions` - Create recurring transaction
- `GET /api/v1/recurring-transactions/{id}` - Get recurring transaction
- `PATCH /api/v1/recurring-transactions/{id}` - Update recurring transaction
- `DELETE /api/v1/recurring-transactions/{id}` - Delete recurring transaction
- `POST /api/v1/recurring-transactions/{id}/execute` - Execute manually

### Analytics
- `GET /api/v1/analytics/spending-by-category` - Spending by category
- `GET /api/v1/analytics/spending-trend` - Spending trend
- `GET /api/v1/analytics/top-categories` - Top categories
- `GET /api/v1/reports/transactions.csv` - Export CSV
- `GET /api/v1/reports/transactions.pdf` - Export PDF

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app tests/
```

## Clean Code Principles

This project follows strict clean code principles:

1. **3-Layer Architecture** - Separation of concerns
2. **Small Functions** - Each function does one thing
3. **No If-Else Hell** - Early returns, helper methods
4. **Clear Naming** - Descriptive variable/function names
5. **DTOs** - Pydantic schemas for all requests/responses
6. **Error Handling** - Proper HTTP exceptions with clear messages
7. **Testability** - Services are easily testable in isolation

## Database Schema

- **users** - User accounts
- **wallets** - User wallets/accounts
- **categories** - Transaction categories
- **transactions** - Financial transactions
- **budgets** - Budget limits by category
- **recurring_transactions** - Recurring transaction templates

## Development

### Create New Migration

```bash
alembic revision --autogenerate -m "description"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## License

MIT