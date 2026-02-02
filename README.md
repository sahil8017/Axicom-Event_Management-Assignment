# Event Management System

A full-stack event management application built with FastAPI and vanilla JavaScript.

## Features

- **Multi-role Authentication**: Admin, Vendor, and User roles with JWT-based authentication
- **Admin Dashboard**: Manage users, vendors, memberships, and approve/reject products
- **Vendor Dashboard**: Add products/services, manage orders, and view status
- **User Dashboard**: Browse vendors, add to cart, place orders, and manage guest lists

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: JWT with python-jose

## Quick Start

### 1. Clone and Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional for development)
```

### 3. Run the Application

```bash
cd backend
uvicorn main:app --reload
```

The application will be available at: **http://localhost:8000**

## Default Credentials

> ⚠️ **Change these in production!**

| Role   | Email            | Password  |
|--------|------------------|-----------|
| Admin  | admin@admin.com  | admin123  |

## Environment Variables

| Variable                   | Description                          | Default                          |
|----------------------------|--------------------------------------|----------------------------------|
| `SECRET_KEY`               | JWT signing secret key               | (required in production)         |
| `DATABASE_URL`             | Database connection string           | `sqlite:///./event_management.db`|
| `CORS_ORIGINS`             | Allowed CORS origins (comma-separated)| `*`                             |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration in minutes    | `1440` (24 hours)               |
| `DEBUG`                    | Enable debug mode                    | `true`                          |

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
├── backend/
│   ├── main.py           # FastAPI application entry point
│   ├── auth.py           # Authentication utilities (JWT, password hashing)
│   ├── database.py       # Database configuration
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   └── routers/
│       ├── auth.py       # Authentication endpoints
│       ├── admin.py      # Admin endpoints
│       ├── vendor.py     # Vendor endpoints
│       └── user.py       # User endpoints
├── frontend/
│   ├── index.html        # Landing page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── admin-dashboard.html
│   ├── vendor-dashboard.html
│   ├── user-dashboard.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── api.js        # API client utilities
├── .env                  # Environment variables (not in git)
├── .env.example          # Environment template
├── .gitignore
├── requirements.txt
└── README.md
```

## API Endpoints Overview

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - Register new user
- `POST /api/auth/register-vendor` - Register as vendor
- `GET /api/auth/me` - Get current user info

### Admin
- `GET /api/admin/users` - List all users
- `POST/PUT/DELETE /api/admin/users/{id}` - Manage users
- `GET /api/admin/vendors` - List all vendors
- `PUT /api/admin/memberships/{id}` - Update vendor membership
- `GET /api/admin/items` - List all products
- `PUT /api/admin/items/{id}/approve` - Approve product
- `PUT /api/admin/items/{id}/reject` - Reject product

### Vendor
- `GET/POST/PUT/DELETE /api/vendor/items` - Manage products
- `GET /api/vendor/requests` - View orders
- `PUT /api/vendor/requests/{id}` - Update order status
- `GET /api/vendor/profile` - Get vendor profile

### User
- `GET /api/user/vendors` - Browse active vendors
- `GET /api/user/vendors/{id}/items` - Get vendor products
- `GET/POST/DELETE /api/user/cart` - Manage cart
- `GET/POST /api/user/orders` - Manage orders
- `PUT /api/user/orders/{id}/pay` - Pay for order
- `PUT /api/user/orders/{id}/cancel` - Cancel order
- `GET/POST/PUT/DELETE /api/user/guests` - Manage guest list

## License

MIT License
