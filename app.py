from flask import Flask, render_template_string, request, redirect, url_for, session
import json
import os
import shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pacific_times_secret_key"

DATA_FILE = "books.json"
BACKUP_FOLDER = "backups"

DEFAULT_BOOKS = [
    {
        "id": 1,
        "title": "The Silent Library",
        "author": "Ava Hart",
        "category": "Fiction",
        "price": 18.99,
        "inventory": 12,
        "image": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 2,
        "title": "Pages of Autumn",
        "author": "Liam Cole",
        "category": "Romance",
        "price": 15.49,
        "inventory": 7,
        "image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 3,
        "title": "Moonlit Stories",
        "author": "Nora Blake",
        "category": "Mystery",
        "price": 21.00,
        "inventory": 4,
        "image": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 4,
        "title": "Hidden Chapters",
        "author": "Ethan Wells",
        "category": "Non-Fiction",
        "price": 17.75,
        "inventory": 10,
        "image": "https://images.unsplash.com/photo-1524578271613-d550eacf6090?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 5,
        "title": "City of Lanterns",
        "author": "Ava Hart",
        "category": "Mystery",
        "price": 19.25,
        "inventory": 5,
        "image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": 6,
        "title": "Wildflower Letters",
        "author": "Nora Blake",
        "category": "Romance",
        "price": 14.99,
        "inventory": 9,
        "image": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=800&q=80"
    },
]


def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_BOOKS, f, indent=4)


def load_books():
    ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_books(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def backup_books():
    ensure_data_file()

    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(BACKUP_FOLDER, f"books_backup_{timestamp}.json")
    shutil.copy(DATA_FILE, backup_file)


def save_and_backup_books(data):
    save_books(data)
    backup_books()


def restore_latest_backup():
    if not os.path.exists(BACKUP_FOLDER):
        return False, "No backup folder exists."

    backup_files = [
        f for f in os.listdir(BACKUP_FOLDER)
        if f.startswith("books_backup_") and f.endswith(".json")
    ]

    if not backup_files:
        return False, "No backups available to restore."

    backup_files.sort(reverse=True)
    latest_backup = os.path.join(BACKUP_FOLDER, backup_files[0])
    shutil.copy(latest_backup, DATA_FILE)
    return True, f"Restored inventory from {backup_files[0]}."


CUSTOMER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pacific Times Book Market</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        body {
            background: #f4f4f4;
            color: #111111;
        }

        a {
            text-decoration: none;
            color: inherit;
        }

        .topbar {
            background: #111111;
            color: white;
            padding: 14px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        .nav-links {
            display: flex;
            gap: 18px;
            font-size: 15px;
            align-items: center;
        }

        .employee-link {
            background: white;
            color: #111111;
            padding: 8px 14px;
            border-radius: 8px;
            font-weight: bold;
            border: 1px solid #111111;
        }

        .hero {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            align-items: center;
            gap: 30px;
            padding: 60px 50px;
            background: linear-gradient(135deg, #dddddd, #ffffff);
        }

        .hero-text h1 {
            font-size: 52px;
            line-height: 1.1;
            margin-bottom: 18px;
            color: #111111;
        }

        .hero-text p {
            font-size: 18px;
            color: #444444;
            max-width: 520px;
            margin-bottom: 24px;
        }

        .hero-buttons {
            display: flex;
            gap: 14px;
        }

        .btn {
            padding: 14px 22px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 15px;
            font-weight: bold;
        }

        .btn-primary {
            background: #111111;
            color: white;
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid #111111;
            color: #111111;
        }

        .hero-image {
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .hero-image img {
            width: 100%;
            max-width: 430px;
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }

        .section {
            padding: 55px 50px;
        }

        .section-title {
            font-size: 32px;
            color: #111111;
            margin-bottom: 10px;
        }

        .section-subtitle {
            color: #555555;
            margin-bottom: 28px;
        }

        .categories {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 18px;
        }

        .category-card {
            background: white;
            border-radius: 14px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 5px 16px rgba(0,0,0,0.07);
            font-weight: bold;
            color: #222222;
        }

        .search-box {
            background: white;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 5px 16px rgba(0,0,0,0.07);
            margin-bottom: 30px;
        }

        .search-form {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
        }

        .search-form input,
        .search-form select {
            padding: 12px 14px;
            border: 1px solid #cfcfcf;
            border-radius: 8px;
            font-size: 15px;
            width: 100%;
        }

        .search-results-note {
            margin-top: 16px;
            color: #555555;
            font-size: 15px;
        }

        .books-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }

        .book-card {
            background: white;
            border-radius: 14px;
            overflow: hidden;
            box-shadow: 0 5px 16px rgba(0,0,0,0.07);
            transition: transform 0.2s ease;
        }

        .book-card:hover {
            transform: translateY(-4px);
        }

        .book-card img {
            width: 100%;
            height: 280px;
            object-fit: cover;
        }

        .book-info {
            padding: 18px;
        }

        .book-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
            color: #111111;
        }

        .book-author,
        .book-category,
        .inventory {
            color: #555555;
            font-size: 14px;
            margin-bottom: 8px;
        }

        .inventory strong {
            color: #111111;
        }

        .inventory.low-stock {
            color: #a14b2b;
            font-weight: bold;
        }

        .inventory.out-stock {
            color: #9b1c1c;
            font-weight: bold;
        }

        .book-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 10px;
        }

        .price {
            font-weight: bold;
            color: #111111;
        }

        .cart-dropdown {
            position: relative;
            display: inline-block;
        }

        .cart-toggle {
            background: #111111;
            color: white;
            padding: 8px 14px;
            border-radius: 8px;
            font-weight: bold;
            border: 1px solid white;
            cursor: pointer;
        }

        .cart-panel {
            display: none;
            position: absolute;
            right: 0;
            top: 42px;
            width: 360px;
            background: white;
            color: #111111;
            border-radius: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            padding: 18px;
            z-index: 1000;
        }

        .cart-panel.open {
            display: block;
        }

        .cart-panel-title {
            font-size: 20px;
            font-weight: bold;
            color: #111111;
            margin-bottom: 14px;
        }

        .cart-mini-row {
            display: grid;
            grid-template-columns: 1.6fr .8fr .8fr;
            gap: 10px;
            padding: 10px 0;
            border-bottom: 1px solid #e8e8e8;
            align-items: center;
            font-size: 14px;
        }

        .cart-mini-header {
            font-weight: bold;
            color: #111111;
        }

        .cart-mini-total {
            margin-top: 14px;
            text-align: right;
            font-weight: bold;
            color: #111111;
        }

        .cart-mini-actions {
            margin-top: 14px;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            flex-wrap: wrap;
        }

        .buy-form {
            margin: 0;
        }

        .empty-cart {
            color: #555555;
            padding-top: 8px;
        }

        .newsletter {
            background: #111111;
            color: white;
            border-radius: 20px;
            padding: 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
        }

        .newsletter h3 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .newsletter p {
            color: #d9d9d9;
        }

        .newsletter form {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .newsletter input {
            padding: 14px 16px;
            min-width: 280px;
            border: none;
            border-radius: 8px;
        }

        footer {
            padding: 30px 50px 45px;
            color: #555555;
            text-align: center;
        }

        @media (max-width: 980px) {
            .hero,
            .categories,
            .search-form,
            .books-grid {
                grid-template-columns: 1fr 1fr;
            }
        }

        @media (max-width: 700px) {
            .topbar,
            .hero,
            .newsletter {
                flex-direction: column;
                display: flex;
                text-align: center;
            }

            .nav-links {
                flex-wrap: wrap;
                justify-content: center;
            }

            .hero {
                padding: 40px 24px;
            }

            .section {
                padding: 40px 24px;
            }

            .categories,
            .search-form,
            .books-grid {
                grid-template-columns: 1fr;
            }

            .cart-panel {
                width: 300px;
            }
        }
    </style>
</head>
<body>
    <header class="topbar">
        <div class="logo">Pacific Times Book Market</div>
        <nav class="nav-links">
            <a href="#">Home</a>
            <a href="#search">Search</a>
            <a href="#">Categories</a>
            <a href="#">Contact</a>
            <a class="employee-link" href="/employee-signin">Employee Sign In</a>
            <div class="cart-dropdown">
                <button class="cart-toggle" type="button" onclick="toggleCart()">Cart ({{ cart_count }})</button>
                <div class="cart-panel" id="cartPanel">
                    <div class="cart-panel-title">Shopping Cart</div>
                    {% if cart_items %}
                        <div class="cart-mini-row cart-mini-header">
                            <div>Book</div>
                            <div>Qty</div>
                            <div>Subtotal</div>
                        </div>
                        {% for item in cart_items %}
                        <div class="cart-mini-row">
                            <div>{{ item.title }}</div>
                            <div>{{ item.quantity }}</div>
                            <div>${{ '%.2f'|format(item.subtotal) }}</div>
                        </div>
                        {% endfor %}
                        <div class="cart-mini-total">Total: ${{ '%.2f'|format(cart_total) }}</div>
                        <div class="cart-mini-actions">
                            <form method="POST" action="/clear-cart">
                                <button class="btn btn-secondary" type="submit">Clear</button>
                            </form>
                            <button class="btn btn-primary" type="button">Checkout</button>
                        </div>
                    {% else %}
                        <div class="empty-cart">Your cart is empty.</div>
                    {% endif %}
                </div>
            </div>
        </nav>
    </header>

    <section class="hero">
        <div class="hero-text">
            <h1>Discover your next favorite book</h1>
            <p>Browse trending titles, timeless classics, and search live inventory by title, author, or category.</p>
            <div class="hero-buttons">
                <button class="btn btn-primary">Shop Now</button>
                <button class="btn btn-secondary">View Collection</button>
            </div>
        </div>
        <div class="hero-image">
            <img src="https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80" alt="Books">
        </div>
    </section>

    <section class="section">
        <h2 class="section-title">Browse Categories</h2>
        <p class="section-subtitle">Find books by the genres you love most.</p>
        <div class="categories">
            <div class="category-card">Fiction</div>
            <div class="category-card">Romance</div>
            <div class="category-card">Mystery</div>
            <div class="category-card">Non-Fiction</div>
        </div>
    </section>

    <section class="section" id="search">
        <h2 class="section-title">Search Our Inventory</h2>
        <p class="section-subtitle">Search by title, author, and category to see what is currently in stock.</p>

        <div class="search-box">
            <form class="search-form" method="GET" action="/">
                <input type="text" name="title" placeholder="Search by title" value="{{ title_query }}">
                <input type="text" name="author" placeholder="Search by author" value="{{ author_query }}">
                <select name="category">
                    <option value="">All categories</option>
                    {% for category in categories %}
                        <option value="{{ category }}" {% if category == category_query %}selected{% endif %}>{{ category }}</option>
                    {% endfor %}
                </select>
                <button class="btn btn-primary" type="submit">Search</button>
            </form>
            <div class="search-results-note">Showing <strong>{{ books|length }}</strong> matching book(s).</div>
        </div>
    </section>

    <section class="section" id="inventory">
        <h2 class="section-title">Available Inventory</h2>
        <p class="section-subtitle">Current books on hand based on your search.</p>
        <div class="books-grid">
            {% for book in books %}
            <div class="book-card">
                <img src="{{ book.image }}" alt="{{ book.title }}">
                <div class="book-info">
                    <div class="book-title">{{ book.title }}</div>
                    <div class="book-author">by {{ book.author }}</div>
                    <div class="book-category">Category: {{ book.category }}</div>
                    <div class="inventory {% if book.inventory == 0 %}out-stock{% elif book.inventory <= 2 %}low-stock{% endif %}">
                        <strong>Inventory on hand:</strong> {{ book.inventory }}
                    </div>
                    <div class="book-bottom">
                        <span class="price">${{ '%.2f'|format(book.price) }}</span>
                        <form class="buy-form" method="POST" action="/add-to-cart/{{ book.id }}">
                            <button class="btn btn-primary" type="submit" {% if book.inventory == 0 %}disabled{% endif %}>
                                {% if book.inventory == 0 %}Out of Stock{% else %}Buy{% endif %}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            {% else %}
            <p>No books matched your search.</p>
            {% endfor %}
        </div>
    </section>

    <section class="section">
        <div class="newsletter">
            <div>
                <h3>Join our newsletter</h3>
                <p>Get updates on new arrivals, sales, and curated recommendations.</p>
            </div>
            <form>
                <input type="email" placeholder="Enter your email" />
                <button class="btn btn-primary" type="submit">Subscribe</button>
            </form>
        </div>
    </section>

    <footer>
        <p>© 2026 Pacific Times Book Market. All rights reserved.</p>
    </footer>

    <script>
        function toggleCart() {
            const panel = document.getElementById('cartPanel');
            panel.classList.toggle('open');
        }

        document.addEventListener('click', function(event) {
            const dropdown = document.querySelector('.cart-dropdown');
            if (dropdown && !dropdown.contains(event.target)) {
                const panel = document.getElementById('cartPanel');
                if (panel) {
                    panel.classList.remove('open');
                }
            }
        });
    </script>
</body>
</html>
"""

EMPLOYEE_SIGNIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pacific Times Book Market Employee Sign In</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        body {
            min-height: 100vh;
            background: linear-gradient(135deg, #dbeafe, #ffffff);
            color: #12305b;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }

        .signin-card {
            width: 100%;
            max-width: 440px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.18);
            padding: 32px;
            border: 1px solid #bfdbfe;
        }

        .signin-card h1 {
            font-size: 30px;
            margin-bottom: 12px;
            color: #1d4ed8;
        }

        .signin-card p {
            color: #335c99;
            margin-bottom: 22px;
            line-height: 1.5;
        }

        .signin-form {
            display: grid;
            gap: 14px;
        }

        .signin-form label {
            font-weight: bold;
            color: #1e40af;
            font-size: 14px;
        }

        .signin-form input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #93c5fd;
            border-radius: 10px;
            font-size: 15px;
        }

        .employee-btn {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 13px 16px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }

        .back-link {
            display: inline-block;
            margin-top: 16px;
            color: #1d4ed8;
            font-weight: bold;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="signin-card">
        <h1>Employee Sign In</h1>
        <p>This is the employee access page for Pacific Times Book Market. For now, the sign in form is only a placeholder and does not require a username or password.</p>
        <form class="signin-form" method="POST" action="/employee-dashboard">
            <div>
                <label for="employee_name">Employee Name</label>
                <input id="employee_name" name="employee_name" type="text" placeholder="Enter your name" />
            </div>
            <div>
                <label for="employee_id">Employee ID</label>
                <input id="employee_id" name="employee_id" type="text" placeholder="Enter employee ID" />
            </div>
            <button class="employee-btn" type="submit">Sign In</button>
        </form>
        <a class="back-link" href="/">← Back to customer store</a>
    </div>
</body>
</html>
"""

EMPLOYEE_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Pacific Times Book Market Employee Dashboard</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }

        body {
            background: #eff6ff;
            color: #12305b;
            padding: 32px;
        }

        .employee-header {
            background: #2563eb;
            color: white;
            border-radius: 18px;
            padding: 24px 28px;
            margin-bottom: 24px;
        }

        .employee-header h1 {
            font-size: 32px;
            margin-bottom: 10px;
        }

        .employee-header p {
            color: #dbeafe;
        }

        .employee-actions {
            margin-top: 16px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .employee-actions a,
        .employee-actions form button {
            display: inline-block;
            background: white;
            color: #1d4ed8;
            padding: 10px 14px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            border: none;
            cursor: pointer;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 24px;
            align-items: start;
        }

        .inventory-panel,
        .invoice-panel {
            background: white;
            border: 1px solid #bfdbfe;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 10px 24px rgba(37, 99, 235, 0.08);
        }

        .inventory-panel h2,
        .invoice-panel h2 {
            color: #1d4ed8;
            margin-bottom: 18px;
        }

        .inventory-row {
            display: grid;
            grid-template-columns: 2fr 1.2fr 1fr 1fr;
            gap: 12px;
            padding: 14px 0;
            border-bottom: 1px solid #dbeafe;
            align-items: center;
        }

        .inventory-row.header {
            font-weight: bold;
            color: #1e40af;
        }

        .invoice-form {
            display: grid;
            gap: 14px;
        }

        .invoice-form label {
            font-weight: bold;
            color: #1e40af;
            font-size: 14px;
        }

        .invoice-form input,
        .invoice-form select {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #93c5fd;
            border-radius: 10px;
            font-size: 15px;
        }

        .employee-btn {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 13px 16px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }

        .invoice-note {
            margin-top: 10px;
            font-size: 14px;
            color: #335c99;
            line-height: 1.5;
        }

        .success-banner {
            background: #dbeafe;
            color: #1e40af;
            border: 1px solid #93c5fd;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 18px;
            font-weight: bold;
        }

        @media (max-width: 900px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 700px) {
            .inventory-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="employee-header">
        <h1>Employee Dashboard</h1>
        <p>Signed in as {{ employee_name if employee_name else 'Store Employee' }}. This area uses a blue and white theme for employee tools.</p>
        <div class="employee-actions">
            <a href="/">Return to customer storefront</a>
            <form method="POST" action="/restore-backup">
                <input type="hidden" name="employee_name" value="{{ employee_name }}" />
                <button type="submit">Restore Latest Backup</button>
            </form>
        </div>
    </div>

    {% if restock_message %}
    <div class="success-banner">{{ restock_message }}</div>
    {% endif %}

    <div class="dashboard-grid">
        <div class="inventory-panel">
            <h2>Current Inventory Overview</h2>
            <div class="inventory-row header">
                <div>Title</div>
                <div>Author</div>
                <div>Category</div>
                <div>Inventory</div>
            </div>
            {% for book in books %}
            <div class="inventory-row">
                <div>{{ book.title }}</div>
                <div>{{ book.author }}</div>
                <div>{{ book.category }}</div>
                <div>{{ book.inventory }}</div>
            </div>
            {% endfor %}
        </div>

        <div class="invoice-panel">
            <h2>Receive Invoice / Add Inventory</h2>
            <form class="invoice-form" method="POST" action="/employee-restock">
                <input type="hidden" name="employee_name" value="{{ employee_name }}" />
                <div>
                    <label for="book_id">Select Book</label>
                    <select id="book_id" name="book_id" required>
                        {% for book in books %}
                        <option value="{{ book.id }}">{{ book.title }} — current stock: {{ book.inventory }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div>
                    <label for="invoice_number">Invoice Number</label>
                    <input id="invoice_number" name="invoice_number" type="text" placeholder="Enter invoice number" />
                </div>
                <div>
                    <label for="quantity_received">Quantity Received</label>
                    <input id="quantity_received" name="quantity_received" type="number" min="1" placeholder="Enter quantity received" required />
                </div>
                <button class="employee-btn" type="submit">Add Inventory</button>
            </form>
            <div class="invoice-note">
                When an employee receives an invoice shipment, this adds new stock into inventory. Because both the employee and customer pages use the same shared book list, the updated count appears in both views.
            </div>
        </div>
    </div>
</body>
</html>
"""


def get_books():
    return load_books()


def build_cart_data():
    books = get_books()
    cart = session.get("cart", {})
    cart_items = []
    cart_total = 0
    cart_count = 0

    for book in books:
        book_id = str(book["id"])
        if book_id in cart:
            quantity = cart[book_id]
            subtotal = quantity * book["price"]
            cart_items.append({
                "title": book["title"],
                "price": book["price"],
                "quantity": quantity,
                "subtotal": subtotal,
            })
            cart_total += subtotal
            cart_count += quantity

    return cart_items, cart_total, cart_count


@app.route("/")
def home():
    books = get_books()

    title_query = request.args.get("title", "").strip()
    author_query = request.args.get("author", "").strip()
    category_query = request.args.get("category", "").strip()

    filtered_books = []
    for book in books:
        matches_title = title_query.lower() in book["title"].lower() if title_query else True
        matches_author = author_query.lower() in book["author"].lower() if author_query else True
        matches_category = book["category"] == category_query if category_query else True
        if matches_title and matches_author and matches_category:
            filtered_books.append(book)

    categories = sorted({book["category"] for book in books})
    cart_items, cart_total, cart_count = build_cart_data()

    return render_template_string(
        CUSTOMER_HTML,
        books=filtered_books,
        categories=categories,
        title_query=title_query,
        author_query=author_query,
        category_query=category_query,
        cart_items=cart_items,
        cart_total=cart_total,
        cart_count=cart_count,
    )


@app.route("/add-to-cart/<int:book_id>", methods=["POST"])
def add_to_cart(book_id):
    books = get_books()
    cart = session.get("cart", {})
    selected_book = next((book for book in books if book["id"] == book_id), None)

    if selected_book and selected_book["inventory"] > 0:
        cart[str(book_id)] = cart.get(str(book_id), 0) + 1
        selected_book["inventory"] -= 1
        session["cart"] = cart
        save_and_backup_books(books)

    return redirect(url_for("home"))


@app.route("/clear-cart", methods=["POST"])
def clear_cart():
    books = get_books()
    cart = session.get("cart", {})

    for book in books:
        quantity = cart.get(str(book["id"]), 0)
        if quantity:
            book["inventory"] += quantity

    session["cart"] = {}
    save_and_backup_books(books)
    return redirect(url_for("home"))


@app.route("/employee-signin", methods=["GET"])
def employee_signin():
    return render_template_string(EMPLOYEE_SIGNIN_HTML)


@app.route("/employee-dashboard", methods=["POST"])
def employee_dashboard():
    employee_name = request.form.get("employee_name", "").strip()
    books = get_books()
    return render_template_string(
        EMPLOYEE_DASHBOARD_HTML,
        employee_name=employee_name,
        books=books,
        restock_message="",
    )


@app.route("/employee-restock", methods=["POST"])
def employee_restock():
    books = get_books()

    employee_name = request.form.get("employee_name", "").strip()
    book_id = request.form.get("book_id", "").strip()
    invoice_number = request.form.get("invoice_number", "").strip()
    quantity_received = request.form.get("quantity_received", "0").strip()

    restock_message = ""

    try:
        book_id_int = int(book_id)
        quantity_int = int(quantity_received)
    except ValueError:
        book_id_int = None
        quantity_int = 0

    selected_book = next((book for book in books if book["id"] == book_id_int), None)

    if selected_book and quantity_int > 0:
        selected_book["inventory"] += quantity_int
        save_and_backup_books(books)

        if invoice_number:
            restock_message = f"Invoice {invoice_number} processed. Added {quantity_int} unit(s) to {selected_book['title']}."
        else:
            restock_message = f"Added {quantity_int} unit(s) to {selected_book['title']}."
    else:
        restock_message = "Inventory update could not be completed. Please enter a valid quantity."

    return render_template_string(
        EMPLOYEE_DASHBOARD_HTML,
        employee_name=employee_name,
        books=get_books(),
        restock_message=restock_message,
    )


@app.route("/restore-backup", methods=["POST"])
def restore_backup():
    employee_name = request.form.get("employee_name", "").strip()
    success, message = restore_latest_backup()

    return render_template_string(
        EMPLOYEE_DASHBOARD_HTML,
        employee_name=employee_name,
        books=get_books(),
        restock_message=message,
    )


if __name__ == "__main__":
    ensure_data_file()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    