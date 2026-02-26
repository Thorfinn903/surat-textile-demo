# 🏗️ Surat Textile B2B Nexus — Enterprise SaaS Backend

[![Flask](https://img.shields.io/badge/Flask-2.3+-black.svg?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7+-red.svg?style=for-the-badge&logo=redis)](https://redis.io/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg?style=for-the-badge&logo=python)](https://python.org/)

> **Comprehensive Documentation for a Production-Ready B2B Marketplace.**
> This project implements industry-standard architectural patterns for high-scale commerce, featuring automated decision intelligence and enterprise-grade security.

---

## 📖 Table of Contents
- [Project Overview](#-project-overview)
- [Enterprise Feature Set](#-enterprise-feature-set)
- [Decision Intelligence & Analytics](#-decision-intelligence--analytics)
- [Technology Stack](#-technology-stack)
- [System Infrastructure & Directory Structure](#-system-infrastructure--directory-structure)
- [Getting Started](#-getting-started)
- [API Documentation (Swagger)](#-api-documentation-swagger)
- [Testing & CI/CD Pipeline](#-testing--cicd-pipeline)
- [Security Implementation](#-security-implementation)

---

## 🌟 Project Overview
**Textile B2B Nexus** is a modular SaaS platform engineered for the Surat textile manufacturing hub. It facilitates digital transformation for traditional wholesalers by providing a high-performance, mobile-first marketplace.

The system is built on an **N-Tier Architecture**, ensuring clear separation between business logic, data persistence, and the presentation layer. It focuses on large-scale inventory management and real-time lead generation.

---

## 🚀 Enterprise Feature Set
1.  **Modular Monolith Architecture:** Implements a decoupled structure using Flask Blueprints and a strict Service-Layer pattern.
2.  **Stateful Inventory Management:** High-speed stock status synchronization via **AJAX**, ensuring atomic updates without page refreshes.
3.  **Automated Business Logic:** Integrated systems for identifying top-performing categories and stagnant inventory.
4.  **Advanced Analytics Suite:** Interactive visualization of lead velocity, category conversion efficiency, and predictive inventory health.
5.  **PWA Core:** Mobile-optimized Progressive Web App with offline manifest support and SEO-ready infrastructure.
6.  **Backend Optimization:**
    *   **Rate Limiting:** Granular traffic control via Flask-Limiter to prevent resource abuse.
    *   **Data Integrity:** Strict schema validation using **Marshmallow**.
    *   **Performance Caching:** Highly optimized catalog discovery using **Redis**-backed memoization.
    *   **Authentication:** Multi-role access control (RBAC) with session encryption.

---

## 🧠 Decision Intelligence & Analytics
The platform leverages data-driven insights to optimize business operations:
-   **Inventory Health Monitoring:** A dynamic metric representing the ratio of active vs. stagnant inventory, allowing for data-backed procurement decisions.
-   **Dead Stock Identification:** Automated detection of products with high impressions but zero conversions (>10 views, 0 clicks), flagging them for immediate inventory adjustment.
-   **Category Conversion Analysis:** Calculates the efficiency of each product category (`whatsapp_leads / product_views`) to prioritize high-ROI manufacturing lines.

---

## 🛠️ Technology Stack
| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | Python 3.11+ / Flask | Agile development with high extensibility |
| **Persistence Layer** | PostgreSQL / SQLite | Relational data integrity for complex B2B schemas |
| **Distributed Cache** | Redis | Sub-10ms response times for metadata and session storage |
| **Schema Validation** | Marshmallow | Formalized data contracts between frontend and backend |
| **API Standards** | Swagger / OpenAPI 3.0 | Facilitates seamless integration for mobile applicatons |
| **Testing Framework** | Pytest / Coverage | Ensures codebase stability and prevents regression |
| **Frontend Strategy** | Jinja2 / AJAX / CSS3 | Fast-loading, server-side rendered UI with partial dynamic updates |

---

## 📂 System Infrastructure & Directory Structure
```text
.
├── app/                        # Core Application Module
│   ├── config/                 # Environment-specific Configurations
│   ├── namespaces/             # Domain-Driven Blueprints (Modular Units)
│   │   ├── admin/              # ERP Logic & Admin Dashboard
│   │   ├── api/v1/             # RESTful JSON Services
│   │   ├── auth/               # Access Control & Identity Management
│   │   ├── catalog/            # Discovery & Filtering Engine
│   │   └── public/             # Public Route Handlers
│   ├── utils/                  # Shared Utility Functions (JWT, Logging)
│   ├── models.py               # Centralized Data Models (SQLAlchemy)
│   ├── extensions.py           # Pluggable Component Initialization
│   └── __init__.py             # Application Factory Implementation
├── static/                     # Assets & Web Manifests
├── templates/                  # Component-oriented Jinja2 Layouts
├── migrations/                 # Schema Versioning (Alembic)
├── tests/                      # Unit & Integration Test Suites
├── docs/                       # API Specifications & Postman Collections
├── instance/                   # Runtime Files (Local Database)
└── app.py                      # Global Execution Entrypoint
```

---

## 🛠️ Getting Started

### 1. Environment Initialization
```bash
git clone https://github.com/Thorfinn903/surat-textile-demo.git
cd surat-textile-demo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Preparation
```bash
flask db upgrade
python bulk_factory_real.py  # Seed the database with 100+ realistic entities
```

### 3. Execution
```bash
python app.py
```
*   **Production Dashboard:** `http://localhost:5000/admin` (Seed Admin: `admin` / `admin123`)

---

## 🧪 Testing & CI/CD Pipeline
The project enforces a strict stability policy through automated quality assurance.
-   **Test Execution:** Run `pytest --cov=app` to initiate the suite.
-   **CI Integration:** GitHub Actions automate the testing process on every pull request to ensure architectural integrity.
-   **Database Mocking:** Tests utilize an isolated, in-memory database to ensure zero-side-effect execution.

---

## 🔒 Security Implementation
-   **Infrastructure Hardening:** Rate limiting applied to all sensitive authentication endpoints.
-   **Input Sanitization:** Native SQL-injection mitigation via the SQLAlchemy ORM layer.
-   **Cryptographic Security:** High-entropy password hashing using PBKDF2.
-   **Role-Based Security:** Custom decorators implemented to enforce strict authorization across administrative namespaces.

---
© 2026 Surat Textile Nexus — Engineered for Enterprise Scale.