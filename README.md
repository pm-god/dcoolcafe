# ☕ D Cool Cafe - Official Website

> *"A vintage vibe, delicious food, friendly service, passionate team & Fun Experience."*  
> — Official Instagram: [@d_cool_cafe](https://www.instagram.com/d_cool_cafe/)

Official web application for **D Cool Cafe**, the beloved student hangout, coffee adda, and casual dining spot located in **Daily Market, Near NAC Office (Above Goocool), Burla, Sambalpur, Odisha - 768017**.

---

## 🌟 Key Features

1. **Brand Identity & Vintage Aesthetic**:
   - Crafted around the vintage cafe vibe, warm amber glow, and coffeehouse charm.
   - Highlights the cafe's authentic Instagram motto and direct link to [@d_cool_cafe](https://www.instagram.com/d_cool_cafe/).
   - Real-time **Open / Closed** indicator showing current Indian Standard Time (IST) operational status (11:30 AM – 10:30 PM).

2. **Digital Menu & Direct WhatsApp Ordering**:
   - Categorized menu with instant filtering: Signature Coffees, Burgers, Stone-baked Pizzas, Pastas, Loaded Fries & Quick Bites, Mocktails, and Shakes.
   - Live dietary indicators (Pure Veg / Non-Veg), Chef Bestseller badges, and spice levels.
   - **Order Builder / Dynamic Cart**: Add items, adjust quantities, enter customer name, choose Dine-in (Table Number) or Takeaway Parcel, and click **"Send Order on WhatsApp"** to generate a formatted WhatsApp message directly to the cafe team.

3. **Online Table Reservation System**:
   - Book tables for 1 to 15+ guests.
   - Select date, time slot, occasion (Birthday Celebration, Date Night, Exam Farewell, Squad Adda), and special requests (cake arrangements, fairy lights, music).
   - Generates digital confirmation pass (`#DCC-XXXX`) and one-click WhatsApp confirmation.

4. **Instagram Wall & Vintage Lightbox Gallery**:
   - Curated aesthetic showcase of cafe moments, cold coffees, latte art, pizza pulls, and cozy corners.
   - Interactive modal lightbox for inspecting photos.
   - Follow CTA for [@d_cool_cafe](https://www.instagram.com/d_cool_cafe/).

5. **Customer Reviews & Testimonials**:
   - Real community reviews from VSSUT students, VIMSAR medicos, and Burla locals.
   - Interactive review modal where visitors can submit their own ratings and thoughts.

6. **Operations Management Dashboard (`/admin`)**:
   - Staff login with secure session authentication (Default: `admin` / `dcool123`).
   - Manage incoming table reservations with one-click status confirmation (`Confirmed`, `Cancelled`) and direct WhatsApp customer contact.
   - Add new menu items dynamically or toggle availability (In Stock / Out of Stock).
   - Review management and customer inquiry tracker.

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.9+ (Python 3.11 recommended)
- `Flask>=3.0.0`

### 2. Run the Website
Simply run:
```bash
python run.py
```
Or with standard Flask:
```bash
python app.py
```

Open your browser at:
```
http://127.0.0.1:5000
```

### 3. Staff Admin Dashboard
Visit:
```
http://127.0.0.1:5000/admin
```
- **Username:** `admin`
- **Password:** `dcool123`

---

## 📁 Project Architecture

```
dcoolcafe/
├── app.py                     # Main Flask application & REST endpoints
├── database.py                # SQLite schema, tables & initial seed data
├── run.py                     # Intelligent startup script with port auto-detection
├── requirements.txt           # Python dependencies
├── dcoolcafe.db               # SQLite database (auto-generated)
├── static/
│   ├── css/
│   │   └── style.css          # Vintage cafe styling, responsive layout
│   └── js/
│       └── main.js            # Cart logic, WhatsApp dispatch, modals & AJAX
└── templates/
    ├── base.html              # Core layout (Header, Navbar, Cart drawer, Footer)
    ├── index.html             # Homepage with Hero, Adda vibe, Bestsellers, Reviews
    ├── menu.html              # Full interactive menu with categories & search
    ├── reserve.html           # Table reservation booking page
    ├── reserve_success.html   # Reservation confirmation ticket
    ├── gallery.html           # Dedicated Instagram gallery with Lightbox
    ├── about.html             # Our Story, heritage & 4 pillars
    ├── contact.html           # Timings, contact form & Google Maps directions
    └── admin/
        ├── login.html         # Staff login page
        └── dashboard.html     # Bookings, Menu & Inquiries admin panel
```

---

## 📍 Location & Contact Details
- **Address:** Daily Market, Near NAC Office (Above Goocool), Burla, Sambalpur, Odisha - 768017
- **Timings:** Monday to Sunday: 11:30 AM – 10:30 PM
- **Instagram:** [https://www.instagram.com/d_cool_cafe/](https://www.instagram.com/d_cool_cafe/)
