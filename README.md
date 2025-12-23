# Threat Monitoring & Alert Management Platform 🛡️

A scalable, secure backend system designed for ingesting security threats and managing alerts for Next-Gen AI-powered surveillance solutions. Built with **Django REST Framework** and **PostgreSQL**, fully containerized with **Docker**.

## 🚀 Overview

This platform serves as a centralized backend for:
- Ingesting security events from various sources (Firewalls, IDS, AI Models).
- Automatically analyzing event severity.
- generating alerts for High/Critical threats.
- Managing alert lifecycles via a Role-Based Access Control (RBAC) system.

## ✨ Features

- **🔐 Robust Authentication**: Secure JWT (JSON Web Token) authentication.
- **bust Role-Based Access Control (RBAC)**:
    - **Admin**: Full access to manage alerts, users, and system status.
    - **Analyst**: Read-only access to alerts; authorized to ingest new security events.
- **⚡ Automated Alerting**: Intelligent signals automatically promote `HIGH` and `CRITICAL` events to Alerts.
- **📡 RESTful API**: Clean, versioned APIs with pagination, filtering, and search capabilities.
- **🐳 Dockerized**: Production-ready `docker-compose` setup with PostgreSQL integration.
- **🧪 Comprehensive Testing**: over 20+ unit and integration tests covering edge cases and security boundaries.
- **📚 Documentation**: Integrated Swagger/OpenAPI UI.

## 🛠️ Tech Stack

- **Backend Framework**: Python 3.11 + Django 5.0
- **API Toolkit**: Django REST Framework (DRF)
- **Database**: PostgreSQL 15
- **Authentication**: `simplejwt`
- **Containerization**: Docker & Docker Compose
- **Server**: Gunicorn

## ⚙️ Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.
- (Optional) [Postman](https://www.postman.com/) for API testing.

## 🏃 Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd threat_platform
```

### 2. Build and Run
Use Docker Compose to build the containers and start the services.
```bash
docker-compose up --build
```
The application will be available at `http://localhost:8000`.

### 3. Create Admin User
To access the admin panel or perform privileged API actions, create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

## 📖 API Documentation

The project includes auto-generated Swagger documentation.

- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **ReDoc**: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Key Endpoints

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| **Auth** | | | |
| `POST` | `/api/auth/register/` | Register a new analyst | Any |
| `POST` | `/api/auth/login/` | Obtain JWT Access/Refresh tokens | Any |
| `POST` | `/api/auth/refresh/` | Refresh Access token | Any |
| **Events** | | | |
| `POST` | `/api/events/` | Ingest a new security event | Auth Required |
| **Alerts** | | | |
| `GET` | `/api/alerts/` | List all alerts (Filterable) | Auth Required |
| `GET` | `/api/alerts/{id}/` | Get alert details | Auth Required |
| `PATCH` | `/api/alerts/{id}/status/` | Update alert status | **Admin Only** |

### 🔍 Filtering & Search
The Alert List API supports powerful filtering:
- **Filter**: `?status=OPEN` or `?event__severity=HIGH`
- **Search**: `?search=malware` (Searches source, event type, and description)
- **Ordering**: `?ordering=-created_at` (Newest first)

## 🧪 Testing

The project includes a rigorous test suite covering user flows, permissions, and validation edge cases.

To run the tests inside the container:
```bash
docker-compose exec web python manage.py test
```

**Coverage Includes:**
- ✅ User Registration & Login
- ✅ Permission enforcement (Analyst vs Admin)
- ✅ Automatic Alert generation logic
- ✅ Data validation & Boundary testing
- ✅ Pagination & Search functionality

## 📂 Project Structure

```
.
├── config/                 # Project configuration (settings, urls, wsgi)
├── users/                  # Custom User model & Authentication logic
├── monitoring/             # Event & Alert Core Logic
│   ├── models.py           # Database schemas
│   ├── signals.py          # Auto-alert generation logic
│   ├── permissions.py      # Custom permissions (IsAdminOrReadOnly)
│   ├── tests.py            # Integration tests
│   └── views.py            # API Controllers
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Service orchestration
├── requirements.txt        # Python dependencies
└── start.sh                # Entrypoint script
```

## 🧩 Assumptions & Design Decisions

1.  **Separation of Concerns**: Events are raw logs; Alerts are actionable items. They are decoupled tables linked by Foreign Key.
2.  **Alert Logic**: A `post_save` signal is used to decouple the ingestion API from the business logic of creating alerts. This allows for easier future extensibility (e.g., sending emails on critical alerts).
3.  **Security**:
    - Passwords are hashed (PBKDF2).
    - JWTs are used for stateless auth.
    - CORS is configured to allow local development (configurable via env).

## 📝 Configuration

Environment variables are managed in `.env` (provided in repo for assignment convenience):

```bash
DEBUG=True
SECRET_KEY=...
DATABASE_URL=postgres://postgres:postgres@db:5432/threat_db
```

---
**Cyethack Solutions Private Limited - Django Developer Assignment**
Submitted by: Gaurav
