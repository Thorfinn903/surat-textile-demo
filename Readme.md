# Digital Dukan (v8.0) - Premium B2B Textile Marketplace
> **Architected by:** Biranchi Narayan Mahapatra   
> **Status:** Authorized Release (v8.0)  
> **Aesthetic:** "Antigravity" - Premium Black & Gold (B2B Luxury)  

---

## 1. Executive Summary: The Vision

**Digital Dukan** is a high-fidelity **B2B Digital Showroom** engineered specifically for the Surat Textile Market. It bridges the gap between traditional manufacturing and modern digital commerce.

Unlike standard e-commerce sites, this platform is designed for **Wholesale Discovery**. It emphasizes "Collections" and "Catalogs" over individual item transactions, reflecting how B2B textile trade actually works (bulk inquiries, design sets, and category browsing).

**Key Differentiators:**
*   **App-like Experience:** Single-page feel with instant transitions.
*   **Visual-First Discovery:** High-impact imagery with premium "Ghost Card" and "Banner" UI.
*   **No-Login B2B Cart:** Frictionless inquiry generation via WhatsApp.
*   **Smart Filtering:** Backend-driven logic for sorting by Trends, Bestsellers, and Fabric/Work types.

---

## 2. Key Features (v8.0)

### 2.1 Premium Homepage Experience
*   **Hero Section:** Glassmorphic search bar with instant visual appeal.
*   **Featured Collections:** Large, banner-style cards (Festive, Premium Silk, Trending) with:
    *   **Hover Mode:** Cards lift and shadows deepen on interaction.
    *   **Interactive CTA:** "Explore" arrow animates on hover.
    *   **Smart Linking:** Direct mapping to filtered catalog views (e.g., `work_type=Embroidery`).
*   **Category Discovery:** Sleek, pill-shaped tiles for quick access to Sarees, Kurtis, and Dress Materials.
*   **New Arrivals Feed:** An infinite-scroll style feed of the latest products with "Add to Bag" functionality.

### 2.2 Intelligent Catalog & Search
*   **Advanced Filtering:** 
    *   **Search**: Fuzzy logic matches Product Name, Color, Fabric, or Work Type.
    *   **Sort**: 'Trending' (Views), 'Bestseller' (Inquiries), 'Newest' (ID).
    *   **Badges**: Dynamic 'SOLD OUT' and 'NEW' badges based on stock and recency.
*   **Backend Logic:** All filtering happens in Python (`app.py`) using robust SQLAlchemy queries, ensuring data integrity and SEO-friendly URLs (e.g., `/catalog?sort=trending`).

### 2.3 The "Inquiry Bag" (B2B Cart)
*   **Persistence:** LocalStorage-based cart ensures selections survive page reloads.
*   **WhatsApp Bridge:** The "Checkout" action constructs a pre-formatted message with Design Numbers, allowing buyers to send a formal inquiry directly to the seller's WhatsApp.
*   **Zero Friction:** No account creation required—optimized for rapid B2B decision-making.

---

## 3. Technical Architecture

We adhere to a **Flat Directory Structure** for maximum reliability and ease of deployment on minimal infrastructure.

```text
/Textile_Demo_Site
│
├── app.py                # THE CORE: Flask Application, Routing, DB Models.
├── textile.db            # THE DATA: SQlite Database (Auto-generated).
├── bulk_factory_real.py  # THE FACTORY: Script to generate 100+ realistic demo products.
│
├── /static               # ASSETS
│   ├── /css
│   │   └── style.css     # "Antigravity" Design System (Dark/Light Mode).
│   ├── /js
│   │   └── main.js       # Frontend Logic (Cart, Search, UI Interactions).
│   └── /images           # Optimized WebP/AVIF Product Images.
│
└── /templates            # VIEWS (Jinja2)
    ├── base.html         # Master Layout (Navbar, Footer, Cart Drawer).
    ├── index.html        # Homepage (Feed, Collections, Hero).
    ├── catalog.html      # Filterable Grid View.
    ├── admin.html        # Product Management Interface.
    └── cart_drawer.html  # Slide-out Inquiry Cart.
```

### The Tech Stack
*   **Backend:** Flask (Python 3.10+) - Lightweight, fast, and secure.
*   **Database:** SQLAlchemy + SQLite - Serverless, zero-config data storage.
*   **Frontend:** HTML5 + Jinja2 + Bootstrap 5 (Customized) + Vanilla JS.
*   **Styling:** Custom CSS Variables for Theme Management (Dark Mode Default).

---

## 4. Database Schema (The "Product" Model)

The `Product` model is the single source of truth (`app.py`).

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | Integer | Internal Primary Key. |
| `name` | String | Display Name (e.g., "Royal Banarasi Silk"). |
| `category` | String | "Saree", "Kurti", "Lehenga", etc. |
| `work_type` | String | "Embroidery", "Print", "Zari", "Handwork". |
| `material_type` | String | "Silk", "Cotton", "Georgette", "Linen". |
| `color` | String | Dominant color for search indexing. |
| `price` | Float | (Optional) Wholesale price. |
| `image` | String | Filename in `static/images/`. |
| `views` | Integer | **Analytics**: Used for "Trending" sort. |
| `whatsapp_clicks` | Integer | **Analytics**: Used for "Bestseller" sort. |

---

## 5. Developer Manual

### 5.1 Installation & Setup
1.  **Prerequisites:** Python 3.x installed.
2.  **Install Dependencies:**
    ```bash
    pip install Flask Flask-SQLAlchemy
    ```
3.  **Initialize Data (Optional):**
    To generate dummy data (100+ products):
    ```bash
    python bulk_factory_real.py
    ```
4.  **Run Application:**
    ```bash
    python app.py
    ```
5.  **Access:** Open `http://127.0.0.1:5000` in your browser.

### 5.2 Managing Products
*   **Admin Panel:** Access `/admin` to add individual products.
*   **Database Reset:** Delete `textile.db` and re-run `bulk_factory_real.py` to reset the catalog.

### 5.3 Customization
*   **Theme:** Edit `static/css/style.css`. Change `--accent` to update the Gold brand color.
*   **Images:** Add new images to `static/images/` and reference them in `bulk_factory_real.py` or the Admin panel.

---

## 6. Future Roadmap
*   **User Accounts:** for saving "Wishlists" across devices.
*   **Order History:** for tracking past inquiries.
*   **Multi-Vendor Support:** allowing multiple manufacturers to list on one platform.

---

> **"We didn't just build a website. We built a digital asset class."**