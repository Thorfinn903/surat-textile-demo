# 🧵 Surat Textile Portfolio & Digital Catalog (v2.0)

> **"Digital Dukan" for Surat's Textile Market.**
> A lightweight, high-performance web application designed for textile traders to showcase their Saree/Fabric catalogs globally without sharing heavy WhatsApp attachments.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

## 🌟 Key Features

### 🛍️ Customer Facing (Frontend)
- **Digital Catalog:** Browse Sarees, Lehengas, and Fabrics with high-quality images.
- **Smart Search & Filtering:** Filter by Category (Print, Silk, Cotton) or Price Range.
- [cite_start]**Mobile First Design:** Fully responsive UI optimized for traders viewing on phones[cite: 36, 174].
- **WhatsApp Integration:** Direct "Inquire on WhatsApp" button for every product.
- [cite_start]**Lazy Loading:** Images load only when scrolled to save data and battery[cite: 183].

### 🔐 Admin Panel (Backend)
- **Secure Dashboard:** Login protected area for shop owners.
- **Product Management:** Add, Edit, or Delete products easily.
- **Inquiry Tracker:** Track how many people clicked "Call" or "WhatsApp" for specific items.
- [cite_start]**Auto-Image Compressor:** Automatically converts 50MB+ raw photos into <200KB Optimized WebP images using Pillow[cite: 174].

---

## 🛠️ Tech Stack

* **Backend:** Python (Flask Framework)
* **Database:** SQLite (Lightweight, portable `textile.db`)
* **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
* **Image Processing:** Pillow (PIL) for resizing and WebP conversion
* **Server (Production):** Gunicorn + Nginx (AWS/VPS) or WSGI (PythonAnywhere)

---

## 📂 Project Structure

```text
surat-textile-demo/
│
├── app.py                 # Main Flask Application Entry Point
├── config.py              # Configuration (Client Name, DB Path, Secrets)
├── requirements.txt       # Python Dependencies
├── wsgi.py                # Entry point for Production Servers
│
├── instance/
│   └── textile.db         # SQLite Database (Auto-generated)
│
├── static/
│   ├── css/               # Custom Styles
│   ├── js/                # Scripts (Lazy load, Search logic)
│   └── images/            # Optimized Product Images (WebP)
│
└── templates/
    ├── base.html          # Base Layout (Navbar/Footer)
    ├── index.html         # Main Catalog Page
    ├── admin.html         # Admin Dashboard
    └── login.html         # Secure Login Page