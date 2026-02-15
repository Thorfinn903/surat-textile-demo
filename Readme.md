# 👑 Surat Textile Portfolio & Digital Catalog (v4.1.0)

**"Digital Dukan"** – The Premium Digital Showroom.  
A luxury B2B catalog designed for Surat's textile traders to showcase Saree & Fabric collections with the elegance of a flagship store.

---

## 🌟 What's New in v4.1 (Premium Upgrade)

- **Royal Aesthetics**: A complete UI overhaul featuring a **Deep Maroon (#2c0e0e)** & **Antique Gold (#d4af37)** palette.

- **Typography**: Integrated **'Playfair Display'** for luxury headings and **'Inter'** for clean readability.

- **Unified Command Bar**: Replaced clutter with a single, floating "Airbnb-style" bar for Search & Filtering.

- **App-Like Experience**: Added a **Sticky Bottom Navigation Bar** for mobile users to browse effortlessly.

- **Premium UI Enhancements** ✨:
  - **Glassmorphism Effects**: Frosted glass design with blur effects throughout
  - **Animated Login Page**: Gradient background with floating orbs and shimmer effects
  - **Enhanced Admin Panel**: Staggered card animations with premium styling
  - **Smooth Animations**: Ripple effects, hover lifts, and micro-interactions

---

## 🚀 Key Features

### 🛍️ Customer Facing (Frontend)

- **Unified Search & Filter**: A single floating "Command Bar" to search by Design Number or filter by Category/Work Type instantly.

- **Premium Product Cards**: Borderless design with soft shadows (`box-shadow`) and hover-zoom effects.

- **Mobile-First Navigation**: "Sticky Bottom Nav" for one-thumb access to Home, Trending, and Chat.

- **Smart Trending Grid**: A self-centering, symmetrical 4-column layout that highlights top products.

- **WhatsApp Integration**:
  - **Direct Chat**: "Inquire" button on every product.
  - **Floating Action Button (FAB)**: Smart floating button for quick contact (optimized to not overlap nav).

### 🔐 Admin Panel (Backend)

- **JSON Config System**: Update Shop Name, Address, and Phone Number via `settings.json` without touching code.

- **Enhanced Uploads**: Dropdown menus for Work Type (Embroidery, Print) and Category (Saree, Kurti).

- **Auto-Image Compressor**: Automatically resizes and converts raw uploads (50MB+) into optimized WebP format (<200KB).

- **Secure Session Management**: Built-in secure Logout and Activity Logging.

- **Premium UI**: Glassmorphism cards with staggered animations and gold gradient headers.

---

## 🛠️ Tech Stack

- **Backend**: Python (Flask Framework)
- **Database**: SQLite (Zero-config `textile.db`)
- **Frontend**: HTML5, Bootstrap 5, Custom CSS (Maroon/Gold Theme)
- **Asset Management**: Custom `ASSET_VERSION` cache-busting system.
- **Image Processing**: Pillow (PIL) for WebP conversion.

---

## 📂 Project Structure

```
surat-textile-demo/
│
├── app.py                 # Main Application (Routes + Logic)
├── settings.json          # [NEW] Global Shop Configuration
├── requirements.txt       # Dependencies
│
├── static/
│   ├── css/
│   │   └── style.css      # v4.0 Premium Styles 
│   └── images/            
│
└── templates/
    ├── about.html         # About Us
    ├── contact.html       # Contact Us
    ├── base.html          # Layout
    ├── index.html         # Main Catalog 
    ├── admin.html         # Dashboard 
    └── login.html         # Admin Login
```

---

## ⚙️ Quick Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Shop Details**:  
   Open `settings.json` and update your details:
   ```json
   {
     "shop_name": "Laxmi Pati Sarees",
     "contact_number": "+91 98765 43210",
     "address": "Shop 101, Millennium Market 2, Ring Road, Surat"
   }
   ```

3. **Run the App**:
   ```bash
   python app.py
   ```

4. Visit `http://127.0.0.1:5000` in your browser.

---

## 🎨 UI Highlight: The "Unified Command Bar"

Instead of messy forms, v4.1 uses a single floating element with premium glassmorphism:

```html
<div class="unified-search-bar">
   [ 🔍 Search Input ]  [ Category ⌄ ]  [ Work Type ⌄ ]  [ SEARCH (Gold Button) ]
</div>
```

**Features**:
- Glassmorphism with `backdrop-filter: blur(30px)`
- Gold gradient search button with shimmer effect
- Custom dropdown arrows that change color on hover
- Smooth slide-up animation on page load
- Fully responsive (stacks on mobile)

---

## ✨ Premium Design Features

### Search Bar
- Enhanced glassmorphism with 30px blur
- Gold-accented borders and gradients
- Smooth animations and hover effects
- Custom SVG dropdown arrows
- Mobile-responsive design

### Login Page
- Animated gradient background (purple → violet → pink)
- Floating decorative orbs with rotation
- Glassmorphism card with shimmer effects
- Enhanced form inputs with focus glow
- Ripple button effect

### Admin Panel
- Soft gradient background with gold overlay
- Staggered card animations (0.1s - 0.4s delays)
- Premium glassmorphism cards
- Animated gold headers with shine effect
- Pulsing statistics
- Enhanced table styling with hover effects

---

## 🐛 Troubleshooting

- **Changes not showing?** Update `ASSET_VERSION` in `app.py` and hard refresh (`Ctrl+F5`).

- **Layout leaning left?** Ensure the "Nuclear Centering" CSS block is present in `style.css`.

- **Animations not working?** Check browser compatibility - glassmorphism requires modern browsers (Chrome 76+, Safari 13.1+, Firefox 103+).

---

## 📚 Documentation

For detailed information about the latest UI enhancements, see [UI_ENHANCEMENTS.md](UI_ENHANCEMENTS.md).

---

**Built for the Visionary Textile Leaders of Surat.**  
Developed by **Biranchi Narayan Mahapatra**.