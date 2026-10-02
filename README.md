# Diagnostic Centre Management System - Backend API

A production-ready, containerized Django REST Framework (DRF) backend for a Diagnostic Centre Management System. It features JWT-based authentication, asynchronous webhook processing with Celery and Redis, robust database models, and automated Swagger/OpenAPI documentation.

---

## 1. How to Run the Project Locally

### Prerequisites

* **Docker & Docker Compose** installed on your machine.

### Quick Start Guide

1. **Clone the repository & navigate to the project root:**

   ```bash
   cd "DiagnoFlow"
   ```

2. **Build and start all services via Docker Compose:**

   ```bash
   docker compose up --build -d
   ```

   This spins up PostgreSQL, Redis, and the Django web container concurrently.

3. **Run database migrations:**

   ```bash
   docker compose exec web python manage.py migrate
   ```

4. **Run the automated test suite to verify functionality:**

   ```bash
   docker compose exec web python manage.py test
   ```

5. **Generate the OpenAPI schema:**

   ```bash
   docker compose exec web python manage.py spectacular --file schema.yml
   ```

6. **Access the Interactive API Documentation (Swagger UI):**

   Open your browser and navigate to:

   `http://127.0.0.1:8000/api/docs/`

---

## 2. API Endpoints & Example Requests

### Authentication

#### Register a User

```http
POST /api/auth/signup/
```

#### Obtain JWT Tokens (Login)

```http
POST /api/auth/login/
```

**Request Body:**

```json
{
  "username": "testuser",
  "password": "securepassword123"
}
```

#### Refresh Access Token

```http
POST /api/auth/refresh/
```

---

### Diagnostic Centres & Tests

#### List Centres

```http
GET /api/centres/
```

> Public endpoint.

#### List Tests

```http
GET /api/tests/
```

> Public endpoint.

---

### Bookings & Payments

#### Create Booking

```http
POST /api/bookings/
```

> Requires Bearer Token.

**Request Body:**

```json
{
  "test": 1,
  "centre": 1,
  "appointment_datetime": "2026-06-01T10:00:00Z"
}
```

#### Simulate Payment

```http
POST /api/payments/simulate/
```

> Requires Bearer Token.

**Request Body:**

```json
{
  "booking_id": 1
}
```

#### Payment Webhook

```http
POST /api/payments/webhook/
```

> Idempotent payment webhook endpoint.

**Request Body:**

```json
{
  "event_id": "evt_unique_abc_999",
  "booking_id": 1,
  "status": "SUCCESS"
}
```

---

## 3. Database & Schema Design

### `DiagnosticCentre`

Stores physical location and branch metadata.

### `DiagnosticTest`

Tied to a diagnostic centre via a Foreign Key. Contains:

* Test name
* Description
* Pricing information

### `Booking`

Links a registered user to a specific diagnostic test and centre.

Tracks:

* Appointment timestamp
* Booking lifecycle state

Supported booking states:

* `PENDING`
* `CONFIRMED`
* `FAILED`
* `CANCELLED`

### `Payment`

Linked with bookings.

Enforces transaction tracking and **idempotency support** through a unique `event_id` column. This prevents duplicate processing or double-confirmation when payment gateway webhooks are retried.

---

## 4. Important Assumptions Made

### 1. Stateless Webhooks

Payment gateway webhooks arrive asynchronously and must rely on unique `event_id` values to guarantee idempotent processing.

This prevents:

* Duplicate ledger entries
* Double-confirmation bugs
* Repeated processing of the same payment event

### 2. Containerized Environment

Local development is strictly managed through Docker Compose to maintain consistency with production regarding:

* Python runtime version (`3.12-slim`)
* PostgreSQL
* Redis
* Database drivers
* Message broker configuration

### 3. Sandbox Payment Simulation

A dedicated simulation endpoint is provided for testing purposes to mimic real-world payment gateway callbacks without requiring live third-party payment gateway API keys.

---

## 5. What I Would Improve With More Time

### API Rate Limiting

Implement stricter sliding-window rate limiting using `django-ratelimit` and Redis on sensitive routes such as:

* Authentication endpoints
* Payment endpoints
* Webhook endpoints

This would help mitigate brute-force attempts and excessive request traffic.

### Task Retries & Error Dead-Letter Queues

Enhance Celery webhook background tasks with:

* Explicit retry policies
* Exponential backoff
* Maximum retry limits
* Dead-letter queue handling for persistently failing tasks

### Comprehensive Test Coverage

Expand automated tests to cover additional edge cases, including:

* Concurrent double-booking attempts
* Invalid or expired JWT tokens
* Malformed webhook payloads
* Duplicate webhook events
* Payment retry scenarios
* Database transaction failures

### CI/CD Pipeline Integration

Set up GitHub Actions workflows to automatically:

* Run the test suite
* Validate database migrations
* Check code quality
* Build Docker images
* Run checks on every pull request

---

## 6. Technology Stack

| Component         | Technology                |
| ----------------- | ------------------------- |
| Backend           | Django 6.1                |
| API Framework     | Django REST Framework     |
| Authentication    | Simple JWT                |
| API Documentation | drf-spectacular / OpenAPI |
| Database          | PostgreSQL                |
| Cache             | Redis                     |
| Task Queue        | Celery                    |
| Containerization  | Docker & Docker Compose   |
| Runtime           | Python 3.12               |

---

## 7. Project Architecture

```text
Client
  │
  ▼
Django REST API
  │
  ├── JWT Authentication
  │
  ├── Diagnostic Centres
  │
  ├── Diagnostic Tests
  │
  ├── Bookings
  │
  └── Payments
        │
        ├── Payment Simulation
        │
        └── Webhook
              │
              ▼
           Celery
              │
              ▼
            Redis
              │
              ▼
         PostgreSQL
```

---

## 8. API Documentation

Once the application is running, Swagger UI is available at:

```text
http://127.0.0.1:8000/api/docs/
```

The raw OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

You can also generate the schema manually:

```bash
docker compose exec web python manage.py spectacular --file schema.yml
```

---

## 9. Running Tests

Run the complete Django test suite:

```bash
docker compose exec web python manage.py test
```

To run tests for a specific application:

```bash
docker compose exec web python manage.py test diagnostics
```

---

## 10. Stopping the Application

Stop the running containers:

```bash
docker compose down
```

To remove containers and associated volumes:

```bash
docker compose down -v
```

> **Warning:** Removing volumes will delete the PostgreSQL data stored in the Docker volume.
