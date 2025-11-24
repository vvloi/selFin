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

## Hướng Dẫn Chạy Dự Án (Setup & Installation)

### Bước 0: Tạo Virtual Environment (Khuyến nghị)

```powershell
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# PowerShell:
.\venv\Scripts\Activate.ps1

# CMD:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate
```

**Lưu ý:** Luôn kích hoạt virtual environment trước khi cài đặt packages hoặc chạy dự án!

### Bước 1: Cài Đặt Dependencies

```bash
# Đảm bảo đã activate virtual environment (dòng prompt sẽ có (venv))
# Cài đặt các package cần thiết
pip install -r requirements.txt

# Hoặc cài đặt bản dev (có thêm pytest để test)
pip install -r requirements-dev.txt
```

**Nếu gặp lỗi "No module named pip":**
```powershell
# Download và cài pip
Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py
python get-pip.py
Remove-Item get-pip.py
```

### Bước 2: Cấu Hình Environment

Tạo file `.env` trong thư mục gốc của project:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/finance_db
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=False
```

**Lưu ý:** Thay đổi `postgres:postgres` thành username và password PostgreSQL của bạn.

### Bước 3: Tạo Database

Tạo database PostgreSQL:

```bash
# Sử dụng psql
psql -U postgres
CREATE DATABASE finance_db;
\q

# Hoặc sử dụng pgAdmin để tạo database với tên "finance_db"
```

### Bước 4: Chạy Migration Database

```bash
# Chạy migration để tạo các bảng trong database
alembic upgrade head
```

**Các lệnh migration hữu ích:**

```bash
# Tạo migration mới (khi thay đổi models)
alembic revision --autogenerate -m "mô tả thay đổi"

# Xem lịch sử migrations
alembic history

# Rollback migration gần nhất
alembic downgrade -1

# Rollback tất cả migrations (xóa hết bảng)
alembic downgrade base
```

### Bước 5: Tạo Controllers/Routers từ OpenAPI

**Dự án này đã có sẵn controllers/routers**, nhưng nếu bạn muốn tạo mới hoặc cập nhật từ OpenAPI spec:

**Cách 1: Tạo thủ công theo pattern có sẵn**
- OpenAPI spec: `openapi/finance-api.yaml`
- Tham khảo các router có sẵn trong: `app/api/v1/routers/`
- Mỗi router bao gồm:
  - **Router file** (ví dụ: `auth_router.py`) - định nghĩa endpoints
  - **Service** (`app/services/`) - business logic
  - **Repository** (`app/repositories/`) - database operations
  - **Schema** (`app/schemas/`) - Pydantic models cho request/response

**Cách 2: Sử dụng code generator (nếu cần)**
```bash
# Cài đặt openapi-generator
pip install openapi-generator-cli

# Generate code từ OpenAPI spec
openapi-generator generate -i openapi/finance-api.yaml -g python-fastapi -o generated/
```

**Pattern tạo router mới:**
1. Tạo model trong `app/models/`
2. Tạo schema trong `app/schemas/`
3. Tạo repository trong `app/repositories/`
4. Tạo service trong `app/services/`
5. Tạo router trong `app/api/v1/routers/`
6. Import router vào `app/main.py`

### Bước 6: Khởi Chạy Dự Án

```bash
# Chạy ở chế độ development (auto reload)
uvicorn app.main:app --reload

# Chạy ở port khác
uvicorn app.main:app --reload --port 8001

# Chạy ở production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Sau khi chạy thành công:**

- API sẽ chạy tại: `http://localhost:8000`
- Swagger UI (API Docs): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Bước 7: Test API

**Sử dụng Swagger UI (Recommended):**
1. Mở `http://localhost:8000/docs`
2. Register user: `POST /api/v1/auth/register`
3. Login: `POST /api/v1/auth/login` → lấy token
4. Click "Authorize" → nhập `Bearer {token}`
5. Test các endpoints khác

**Chạy automated tests:**
```bash
# Chạy tất cả tests
pytest

# Chạy với coverage report
pytest --cov=app tests/

# Chạy test cụ thể
pytest tests/test_auth_api.py
```

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