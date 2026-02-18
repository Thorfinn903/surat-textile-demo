# Digital Dukan — Project Chronology

This document tracks the complete evolution of the **Digital Dukan** project, detailing every major version from inception to the current high-performance B2B textile platform.

## **v7.5: The "Antigravity" Restoration** (Current Stable)
**Status:** *Authorized Release*
> **Focus:** Stability, Search Intelligence, & Market Analytics.

*   **Architectural Reset:** Reverted the complex `src/` modularization to a robust **Flat Directory Structure** for maximum reliability and ease of development.
*   **Search Engine 2.0:** Introduced powerful multi-attribute search (Design No, Color, Fabric, Work) using SQLAlchemy fuzzy matching with `OR` logic.
*   **Market Analytics:** Added "Relative Percentage" graphs in the Admin Dashboard to visualize real-time inventory performance without needing complex historical data.
*   **Inventory Logic:** Fixed "Out of Stock" sorting and global counter independence to provide accurate business insights.
*   **Database Upgrade:** Added `color` column to the product schema to support enhanced filtering.

## **v7.4: The Great Refactor Attempt** (Experimental)
**Status:** *Deprecated*
> **Focus:** Enterprise Modularization.

*   **Goal:** Organizing code into a nested `src/` structure with separate blueprints for scalability.
*   **Outcome:** Introduced excessive complexity with import paths and `TemplateNotFound` errors.
*   **Pivot:** Decided that for this specific scale, a monolithic, flat structure offers superior maintainability and developer velocity.

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
