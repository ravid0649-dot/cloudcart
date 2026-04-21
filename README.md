# CloudCart - Production-Style E-commerce PaaS App

CloudCart is a practical full-stack shopping web application built using FastAPI + PostgreSQL + browser frontend and deployable on Render.

## 1) Project Structure

```text
cc2/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── cart.py
│   │       ├── health.py
│   │       ├── orders.py
│   │       ├── products.py
│   │       └── users.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging_config.py
│   │   └── security.py
│   ├── models/
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── cart.py
│   │   ├── order.py
│   │   ├── product.py
│   │   └── user.py
│   ├── static/
│   │   ├── app.js
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── uploads/
│   └── main.py
├── scripts/
│   ├── generate_ppt.py
│   └── seed_data.py
├── .env.example
├── render.yaml
├── requirements.txt
└── README.md
```

## 2) Database Schema

- `users`: user profile + auth metadata + admin role.
- `products`: catalog with category, price, rating, stock, image URL.
- `cart_items`: persistent user cart (`user_id`, `product_id`, `quantity`) with unique user-product constraint.
- `orders`: checkout master record with status (`pending`, `shipped`, `delivered`) and shipping address.
- `order_items`: order line items capturing quantity and unit price at purchase time.

## 3) Backend (FastAPI)

Implemented features:

- JWT signup/login (`/api/auth/signup`, `/api/auth/login`)
- Profile + order history (`/api/users/me`, `/api/users/me/orders`)
- Product browse/search/filter/sort (`/api/products`)
- Cart add/update/remove/persist (`/api/cart`)
- Checkout + order tracking (`/api/orders`, `/api/orders/checkout`)
- Admin dashboard and management (`/api/admin/*`)
- Product image upload (advanced feature) (`/api/admin/products/upload-image`)
- Health endpoint (`/health`)
- Logging and CORS via settings

## 4) Frontend (Basic Working UI)

Served from `app/static`:

- `index.html`: all modules in a single page
- `app.js`: API integration for auth/products/cart/orders/admin
- `styles.css`: clean responsive UI

## 5) Local Setup

1. Create and activate a virtual environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install deps:
   - `pip install -r requirements.txt`
3. Copy env:
   - `cp .env.example .env`
4. Update `DATABASE_URL` in `.env` to your PostgreSQL database.
5. Seed admin + sample products:
   - `python -m scripts.seed_data`
6. Run app:
   - `uvicorn app.main:app --reload`
7. Open:
   - `http://localhost:8000`

## 6) Render Deployment (Step-by-Step)

1. Push this project to GitHub.
2. In Render, click **New +** -> **Blueprint**.
3. Connect your repo and let Render detect `render.yaml`.
4. Render will create:
   - Web service: `cloudcart-web`
   - PostgreSQL: `cloudcart-db`
5. After first deploy, open shell (or local) and seed data:
   - `python -m scripts.seed_data`
6. Visit:
   - `https://<your-web-service>.onrender.com/health`
   - `https://<your-web-service>.onrender.com/`

## 7) Postman / API Testing Guide

1. Signup: `POST /api/auth/signup` body:
   ```json
   { "full_name": "Test User", "email": "user@test.com", "password": "Password@123" }
   ```
2. Login: `POST /api/auth/login` -> copy `access_token`.
3. Set header for protected routes:
   - `Authorization: Bearer <token>`
4. Try:
   - `GET /api/products`
   - `POST /api/cart`
   - `POST /api/orders/checkout`
   - `GET /api/orders`
5. Admin testing:
   - Default seeded admin: `admin@cloudcart.com / Admin@12345`
   - Use `/api/admin/dashboard` and product CRUD routes.

## 8) PPT Generation

A professional, light-themed, 10-slide presentation is generated with:

- `python -m scripts.generate_ppt`

Output:

- `CloudCart_Presentation.pptx`
