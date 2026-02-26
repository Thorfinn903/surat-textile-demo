# Digital Dukan — Project Chronology

This document tracks the complete evolution of the **Digital Dukan** project, detailing every major version from inception to the current high-performance B2B textile platform.

## **v10.0: The "Enterprise Hardening" Release** (Current Stable)
**Status:** *Authorized Release*
> **Focus:** Security, Reliability, & Developer Operations (DevOps).

*   **Elite Testing Suite:** Established a comprehensive **Pytest** framework with session-scoped fixtures and in-memory database isolation for ultra-fast unit/integration tests.
*   **Interactive Documentation:** Integrated **Swagger/OpenAPI** via Flasgger, providing a lived, interactive sandbox for third-party developers to explore and test the API.
*   **Automated CI/CD Pipeline:** Deployed **GitHub Actions** workflows that automatically trigger test suites and coverage reports (Codecov) on every push/pull request.
*   **Advanced Schema Validation:** Switched to **Marshmallow** for robust, schema-based data validation and serialization, eliminating malformed data entry at the API layer.
*   **Infrastructure Rate Limiting:** Implemented **Flask-Limiter** with Redis support to protect the backend from brute-force attacks and bot abuse.

## **v9.0: The "Production Architecture" Scaffold**
**Status:** *Released*

## **v8.0: The Modular Refactor & RBAC**
**Status:** *Released*
> **Focus:** Namespace Isolation & Backend Hardening.

*   **Role-Based Access Control (RBAC):** Implemented custom decorators (`@roles_required`) to secure the Admin Dashboard with granular Sales vs Admin permissions.
*   **Smart Analytics Scoring:** Developed a weighted popularity algorithm `(Views * 1 + Clicks * 5)` to drive more accurate "Trending" product discovery.
*   **Centralized Services:** Moved core database interactions to dedicated `services.py` modules, ensuring DRY (Don't Repeat Yourself) principles across the app.
*   **Alembic Migrations:** Integrated **Flask-Migrate** to handle database schema changes safely via version-controlled migration files.
*   **API v1 Foundation:** Launched a versioned REST API (`/api/v1/`) with standardized JSON response wrappers and JWT-ready authentication hooks.

## **v7.5: The "Hybrid Reset" & Search Engine 2.0**
**Status:** *Released*
> **Focus:** Search Intelligence, Market Analytics, & Structural Optimization.

*   **Architectural Hybrid:** Successfully merged the learnings from the v7.4 modular attempt with a more stable project layout, optimizing import paths and resolving `TemplateNotFound` errors.
*   **Search Engine 2.0:** Introduced powerful multi-attribute search (Design No, Color, Fabric, Work) using SQLAlchemy fuzzy matching with `OR` logic.
*   **Market Analytics:** Added "Relative Percentage" graphs in the Admin Dashboard to visualize real-time inventory performance.
*   **Inventory Logic:** Fixed "Out of Stock" sorting and global counter independence to provide accurate business insights.
*   **Database Upgrade:** Added `color` column to the product schema to support enhanced filtering.

## **v7.0: The "Fluid UX" Update**
**Status:** *Released*
> **Focus:** Speed & Perceived Latency (Zero-Wait Times).

*   **Zero-Latency Modals:** Abandoned separate product detail pages in favor of instant "Quick View" modals.
*   **Data Mule Pattern:** Embedded product data (`data-fabric`, `data-work`) directly into HTML attributes to eliminate extra API round-trips.
*   **Inquiry Bag Generator:** Replaced the standard e-commerce "Cart" with a B2B-focused "Inquiry Generator" that persists locally via `localStorage`, removing the need for user accounts for buyers.

## **v6.0: The Admin Command Center**
**Status:** *Released*
> **Focus:** Inventory Control & Back-Office Efficiency.

*   **Secure Dashboard:** Implemented Flask-Login based authentication for admin access.
*   **Inventory Management:** Created tools for bulk uploading products via CSV and managing stock status (`In Stock` / `Sold Out`).
*   **Activity Logs:** Added secure logging to track who changed stock levels or deleted products.

## **v5.0: The "Invisible Frame" Aesthetic**
**Status:** *Released*
> **Focus:** Branding & Visual Identity.

*   **Dark Mode First:** Established the signature `#121212` deep black theme to reduce eye strain for traders and save battery on mobile devices.
*   **Gold Accents:** Introduced the `#FDCB6E` primary functional color for calls-to-action.
*   **Borderless Cards:** Removed heavy borders in favor of shadow-based depth, creating the premium "floating" look.
*   **Typography:** Switched to the **Inter** font family for modern readability.

## **v4.0: Mobile-First Optimization**
**Status:** *Released*
> **Focus:** Mobile Ergonomics.

*   **44px Touch Targets:** Enforced Apple's Human Interface Guidelines for all buttons and inputs.
*   **Thumb-Zone Navigation:** Introduced the bottom navigation bar for easier one-handed use on large phones.
*   **PWA Foundation:** Added `manifest.json` and basic service worker caching for offline resilience.

## **v3.0: The Smart Filter Engine**
**Status:** *Released*
> **Focus:** Catalog Discovery.

*   **Dynamic Filtering:** Implemented frontend filtering for Categories (Saree, Kurti) and Fabrics.
*   **Visual Feedback:** Added loading states and smooth transitions when filtering products.

## **v2.0: Database Integration**
**Status:** *Released*
> **Focus:** Data Persistence.

*   **SQLite Transition:** Moved from hardcoded HTML product lists to a dynamic SQLite database managed via SQLAlchemy.
*   **Dynamic Routing:** Enabled the application to render product cards dynamically based on database entries.

## **v1.0: Initial Prototype**
**Status:** *Legacy*
> **Focus:** Proof of Concept.

*   **Basic Flask App:** Served simple static HTML pages.
*   **Static Product List:** Hardcoded list of 10-20 products to demonstrate the layout.
*   **Functionality:** Demonstrated the core value proposition: *Direct WhatsApp Inquiries* by linking buttons to the WhatsApp API.
