# 🏛️ System Architecture & Design Rationale

This document serves as a technical deep-dive into the architectural decisions that make **Surat Textile Nexus** a production-ready application.

---

## 1. Modular Namespaces (Blueprints)
Instead of a flat structure, the app is divided into **Namespaces**. This allows for:
-   **Vertical Scaling:** Each module (Admin, API, Catalog) is self-contained with its own `routes.py` and `services.py`.
-   **Domain Isolation:** Changes in the Customer UI won't accidentally break the Admin ERP logic.
-   **Future Microservices:** The folder structure is designed so that the `api/v1` or `admin` modules can be moved to separate repositories with minimal effort.

## 2. The N-Tier Service Layer
Following the **Service-Layer Pattern**, our routes contain Zero business logic.
-   **Routes:** Responsible for parsing request args, handling auth decorators, and returning responses.
-   **Services:** Responsible for DB queries, data aggregation, and complex calculations (e.g., `get_performance_analytics`).
-   **Why?** This makes the code **Unit Testable**. We can test a service function without ever starting a Flask server.

## 3. Decision Intelligence Logic
The system goes beyond CRUD (Create, Read, Update, Delete) by implementing business rules:
-   **Stock Health Calculation:** Uses a velocity-based formula to score inventory quality.
-   **Dead Stock Filter:** A query-level filter that flags low-engagement designs.
-   **Conversion Tracking:** Tracks views vs. clicks at the DB level to calculate ROI per category.

## 4. High-Performance Front-end Patterns
-   **AJAX State Management:** We use a `fetch`-based pattern for inventory toggles. This prevents "Refresh Fatigue" and mimics the experience of a Single Page Application (SPA).
-   **Fragment Caching:** Frequently accessed catalog fragments (like Trending items) are cached in Redis to prevent redundant SQL joins.

## 5. Security Architecture
-   **Rate Limiting:** Implemented at the router level using `Flask-Limiter`.
-   **Schema Validation:** All data entering the system via API is validated against `Marshmallow` schemas, preventing corrupted data from hitting the DB.
-   **Role-Based Access Control (RBAC):** Tiered access for `Admin`, `Staff`, and `Customer` using `Flask-Login` and custom decorators.

## 6. Testing Philosophy
-   **Test Isolation:** Every test run creates a fresh, ephemeral SQLite database in Memory.
-   **Coverage:** Focuses on the **Service Layer** and **API Responses**, as that's where the most critical business logic resides.
-   **CI/CD:** Every commit triggers a GitHub Action that runs the full suite, preventing regressions.

## 7. Configuration Factory
Using the **App Factory Pattern** (`create_app`), the system loads environment-specific configs:
-   **Development:** `SimpleCache`, local logs, SQL logging.
-   **Testing:** In-memory DB, disabled rate limits.
-   **Production:** `PostgreSQL`, `Redis`, Gunicorn workers, and strict security headers.

---

> This architecture ensures that the platform is not just a "demo" but a scalable foundation for a real-world B2B SaaS.
