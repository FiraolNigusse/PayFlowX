# PayFlowX — Payment Simulation & Transaction Engine

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Celery](https://img.shields.io/badge/Celery-Async-orange.svg)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)](https://www.docker.com/)

**PayFlowX** is a high-performance, asynchronous transaction engine designed to simulate the core financial logic of platforms like Stripe and PayPal. This project demonstrates production-level backend engineering, focusing on data integrity, distributed task processing, and financial safety.

---

## 🏛️ Architecture Overview

PayFlowX is built using a **Layered (Clean) Architecture** to ensure a strict separation between HTTP concerns and business logic.

*   **Django API**: Handles request validation, authentication, and job dispatching.
*   **PostgreSQL**: The source of truth, utilizing ACID-compliant transactions and pessimistic locking.
*   **Redis**: Acts as the message broker for the task queue and the caching layer.
*   **Celery Worker**: Processes financial transactions asynchronously to ensure non-blocking API performance.
*   **Flower**: Real-time monitoring for the asynchronous task lifecycle.

---

## 🚀 Key Engineering Features

### 🛡️ Financial Integrity & Safety
*   **Decimal Precision**: Every currency value uses `Decimal` to eliminate floating-point approximation errors inherent in financial math.
*   **Atomic Transactions**: All fund movements follow the "All-or-Nothing" principle. If any part of a transfer fails, the entire state rolls back.
*   **Pessimistic Locking**: Prevents race conditions (like double-spending) by locking wallet rows in the database during balance updates.

### ⚡ Distributed Task Processing
*   **Async Execution**: Heavy transaction logic is offloaded to Celery workers.
*   **Idempotency Keys**: Every transaction request supports an `idempotency_key`. This ensures that network retries never result in duplicate charges.
*   **Retry Strategy**: Implemented exponential backoff for transient failures (e.g., database lock contention).

### 🔐 Identity & Access Control
*   **JWT Authentication**: Stateless authentication using SimpleJWT for horizontal scalability.
*   **RBAC (Role-Based Access Control)**: Distinct permissions for `Users` (transact/view own history) and `Admins` (audit all transactions).

---

## 🏗️ System Design Decisions: The "Why"

| Decision | Rationale |
| :--- | :--- |
| **JWT vs Sessions** | JWTs allow for stateless scaling across multiple container instances without requiring a shared session store. |
| **Service Layer Pattern** | Keeps views "thin." Business logic is encapsulated in pure Python services, making the engine testable and decoupled from the web framework. |
| **Async Processing** | Ensures that the API remains responsive (`<100ms`) even when the engine is performing complex, disk-heavy balance updates. |
| **Idempotency** | In distributed systems, "at-least-once" delivery is common. Idempotency is the only way to guarantee financial safety during client retries. |

---

## 🚦 Getting Started (Docker)

Ensure you have [Docker](https://www.docker.com/) installed.

1.  **Clone and Configure**:
    Create a `.env` file based on the provided examples.
2.  **Spin up the Stack**:
    ```bash
    docker-compose up --build
    ```
3.  **Initialize the Database**:
    In a new terminal:
    ```bash
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py createsuperuser
    ```

---

## 🧪 Demo Walkthrough

Follow this script to see the engine in action:

1.  **Onboard**: Register two users via the `/api/v1/auth/register/` endpoint.
2.  **Fund**: Deposit $500 into User A via `/api/v1/transactions/deposit/`.
3.  **Execute**: Initiate a transfer of $200 from User A to User B via `/api/v1/transactions/transfer/`.
4.  **Observe**: Open **Flower** ([http://localhost:5555](http://localhost:5555)) to watch the `process_transfer_task` move from *Pending* to *Success*.
5.  **Audit**: Log in to the **Admin Panel** ([http://localhost:8000/admin/](http://localhost:8000/admin/)) to verify the updated wallet balances and the immutable transaction ledger.

---

## 📸 Screenshots (Placeholders)

*   **Swagger API Documentation**: (Interactive endpoint testing)
*   **Flower Dashboard**: (Asynchronous task monitoring)
*   **Django Admin**: (The Source of Truth Ledger)

---

## 📈 Future Roadmap

*   **Rate Limiting**: Implementing Redis-based throttling for auth and payment endpoints.
*   **Fraud Detection**: An async service to flag suspicious transaction patterns.
*   **Multi-Currency Support**: Integration with external FX rate providers.
*   **Event-Driven Notifications**: Webhooks or WebSockets to notify users of transaction completion.

---

## 🏁 Final Review Checklist

- [x] API works end-to-end (Auth -> Wallet -> Transfer).
- [x] Async tasks process correctly with Celery/Redis.
- [x] No duplicate transactions via Idempotency Keys.
- [x] Docker setup works from scratch.
- [x] Test suite (Pytest) passes with 100% integrity.

---
*Developed by a Senior Backend Engineer focused on financial reliability.*
