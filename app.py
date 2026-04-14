from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import shutil
from datetime import datetime

app = Flask(__name__)
app.secret_key = "pacific_times_secret_key"

DATA_FILE = "books.json"
BACKUP_FOLDER = "backups"
LOG_FILE = "login_activity.txt"
SALES_LOG_FILE = "sales_log.json"
VENDOR_ORDERS_FILE = "vendor_orders.json"

users_db = {
    "Kristel": "password",
    "Benjamin": "password",
    "Dustyn": "password",
    "Chris": "password",
    "Chandler": "password",
}

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


def ensure_sales_log_file():
    if not os.path.exists(SALES_LOG_FILE):
        with open(SALES_LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def ensure_vendor_orders_file():
    if not os.path.exists(VENDOR_ORDERS_FILE):
        with open(VENDOR_ORDERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def load_books():
    ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_books(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_sales_log():
    ensure_sales_log_file()
    with open(SALES_LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_sales_log(data):
    with open(SALES_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_vendor_orders():
    ensure_vendor_orders_file()
    with open(VENDOR_ORDERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_vendor_orders(data):
    with open(VENDOR_ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def add_vendor_order(vendor_name, book_title, quantity, status="Ordered"):
    orders = load_vendor_orders()

    new_order = {
        "vendor_name": vendor_name,
        "book_title": book_title,
        "quantity": quantity,
        "status": status,
        "order_date": datetime.now().strftime("%Y-%m-%d")
    }

    orders.append(new_order)
    save_vendor_orders(orders)


def get_sale_book_titles(sale):
    return [item.get("title", "") for item in sale.get("items", [])]


def get_sale_authors_from_titles(sale, books):
    title_to_author = {book["title"]: book["author"] for book in books}
    authors = []

    for item in sale.get("items", []):
        title = item.get("title", "")
        author = title_to_author.get(title, "")
        if author:
            authors.append(author)

    return authors


def add_sale_record(customer_name, items, total_price, employee_name="System"):
    sales = load_sales_log()

    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    sale_entry = {
        "order_number": order_number,
        "customer_name": customer_name,
        "employee_name": employee_name,
        "items": items,
        "total_price": round(total_price, 2),
        "sale_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    sales.append(sale_entry)
    save_sales_log(sales)

    return order_number


def get_sales_summary():
    sales = load_sales_log()
    total_orders = len(sales)
    total_revenue = round(sum(sale.get("total_price", 0) for sale in sales), 2)
    return total_orders, total_revenue


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
    return True, "Backup restored successfully."


def log_login(username, success):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "SUCCESS" if success else "FAILURE"

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} | User: {username} | Status: {status}\n")


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
                "id": book["id"],
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

    return render_template(
        "customer.html",
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


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart_items, cart_total, cart_count = build_cart_data()

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        if not customer_name:
            customer_name = "Guest Customer"

        if not cart_items:
            return redirect(url_for("home"))

        sale_items = []
        for item in cart_items:
            sale_items.append({
                "title": item["title"],
                "price": item["price"],
                "quantity": item["quantity"],
                "subtotal": round(item["subtotal"], 2),
            })

        order_number = add_sale_record(
            customer_name=customer_name,
            items=sale_items,
            total_price=cart_total,
            employee_name=session.get("employee_name", "System")
        )

        session["cart"] = {}

        return render_template(
            "checkout_success.html",
            customer_name=customer_name,
            order_number=order_number,
            cart_items=sale_items,
            cart_total=round(cart_total, 2)
        )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        cart_total=round(cart_total, 2),
        cart_count=cart_count
    )


@app.route("/customer-signin", methods=["GET"])
def customer_signin():
    return render_template("customer_signin.html")


@app.route("/customer-dashboard", methods=["POST"])
def customer_dashboard():
    customer_name = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()

    return render_template(
        "customer_dashboard.html",
        customer_name=customer_name,
        customer_email=customer_email,
    )


@app.route("/employee-signin", methods=["GET"])
def employee_signin():
    return render_template("employee_signin.html", error_message="")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if username in users_db and users_db[username] == password:
        log_login(username, True)
        session["employee_name"] = username
        return redirect(url_for("employee_dashboard"))
    else:
        log_login(username if username else "Unknown", False)
        return render_template(
            "employee_signin.html",
            error_message="Login unsuccessful. Please try again."
        )


@app.route("/employee-dashboard", methods=["GET"])
def employee_dashboard():
    employee_name = session.get("employee_name", "Store Employee")
    books = get_books()
    total_orders, total_revenue = get_sales_summary()

    return render_template(
        "employee_dashboard.html",
        employee_name=employee_name,
        books=books,
        restock_message="",
        total_orders=total_orders,
        total_revenue=total_revenue,
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

    total_orders, total_revenue = get_sales_summary()

    return render_template(
        "employee_dashboard.html",
        employee_name=employee_name if employee_name else session.get("employee_name", "Store Employee"),
        books=get_books(),
        restock_message=restock_message,
        total_orders=total_orders,
        total_revenue=total_revenue,
    )


@app.route("/employee-sales-log", methods=["GET"])
def employee_sales_log():
    employee_name = session.get("employee_name", "Store Employee")
    sales = load_sales_log()
    books = get_books()

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    book_query = request.args.get("book", "").strip().lower()
    author_query = request.args.get("author", "").strip().lower()

    filtered_sales = []

    for sale in sales:
        sale_date_str = sale.get("sale_date", "")
        sale_date_only = sale_date_str[:10]

        matches_start = sale_date_only >= start_date if start_date else True
        matches_end = sale_date_only <= end_date if end_date else True

        sale_titles = get_sale_book_titles(sale)
        sale_authors = get_sale_authors_from_titles(sale, books)

        matches_book = any(book_query in title.lower() for title in sale_titles) if book_query else True
        matches_author = any(author_query in author.lower() for author in sale_authors) if author_query else True

        if matches_start and matches_end and matches_book and matches_author:
            sale_copy = sale.copy()
            enriched_items = []

            title_to_author = {book["title"]: book["author"] for book in books}

            for item in sale.get("items", []):
                enriched_item = item.copy()
                enriched_item["author"] = title_to_author.get(item.get("title", ""), "Unknown Author")
                enriched_items.append(enriched_item)

            sale_copy["items"] = enriched_items
            filtered_sales.append(sale_copy)

    filtered_sales = sorted(filtered_sales, key=lambda x: x["sale_date"], reverse=True)

    total_orders = len(filtered_sales)
    total_revenue = round(sum(sale.get("total_price", 0) for sale in filtered_sales), 2)

    return render_template(
        "employee_sales_log.html",
        employee_name=employee_name,
        sales=filtered_sales,
        books=books,
        total_orders=total_orders,
        total_revenue=total_revenue,
        start_date=start_date,
        end_date=end_date,
        book_query=book_query,
        author_query=author_query,
    )


@app.route("/employee-add-sale", methods=["GET", "POST"])
def employee_add_sale():
    employee_name = session.get("employee_name", "Store Employee")
    books = get_books()

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        book_id = request.form.get("book_id", "").strip()
        quantity = request.form.get("quantity", "1").strip()

        try:
            book_id_int = int(book_id)
            quantity_int = int(quantity)
        except ValueError:
            book_id_int = None
            quantity_int = 0

        selected_book = next((book for book in books if book["id"] == book_id_int), None)

        if not customer_name:
            customer_name = "Walk-In Customer"

        if selected_book and quantity_int > 0 and selected_book["inventory"] >= quantity_int:
            selected_book["inventory"] -= quantity_int
            save_and_backup_books(books)

            sale_items = [{
                "title": selected_book["title"],
                "price": selected_book["price"],
                "quantity": quantity_int,
                "subtotal": round(selected_book["price"] * quantity_int, 2),
            }]

            add_sale_record(
                customer_name=customer_name,
                items=sale_items,
                total_price=selected_book["price"] * quantity_int,
                employee_name=employee_name
            )

            return redirect(url_for("employee_sales_log"))

        return render_template(
            "employee_add_sale.html",
            employee_name=employee_name,
            books=books,
            error_message="Could not complete sale. Check quantity and inventory."
        )

    return render_template(
        "employee_add_sale.html",
        employee_name=employee_name,
        books=books,
        error_message=""
    )


@app.route("/employee-vendor-order", methods=["GET", "POST"])
def employee_vendor_order():
    employee_name = session.get("employee_name", "Store Employee")
    books = get_books()

    if request.method == "POST":
        vendor_name = request.form.get("vendor_name", "").strip()
        book_id = request.form.get("book_id", "").strip()
        quantity = request.form.get("quantity", "0").strip()

        try:
            book_id_int = int(book_id)
            quantity_int = int(quantity)
        except ValueError:
            book_id_int = None
            quantity_int = 0

        selected_book = next((book for book in books if book["id"] == book_id_int), None)

        if vendor_name and selected_book and quantity_int > 0:
            add_vendor_order(
                vendor_name=vendor_name,
                book_title=selected_book["title"],
                quantity=quantity_int,
                status="Ordered"
            )
            return redirect(url_for("employee_vendor_orders"))

        return render_template(
            "employee_vendor_order.html",
            employee_name=employee_name,
            books=books,
            error_message="Could not create vendor order. Check all fields."
        )

    return render_template(
        "employee_vendor_order.html",
        employee_name=employee_name,
        books=books,
        error_message=""
    )


@app.route("/employee-vendor-orders", methods=["GET"])
def employee_vendor_orders():
    employee_name = session.get("employee_name", "Store Employee")
    orders = load_vendor_orders()

    return render_template(
        "employee_vendor_orders.html",
        employee_name=employee_name,
        orders=orders
    )


@app.route("/restore-backup", methods=["POST"])
def restore_backup():
    employee_name = request.form.get("employee_name", "").strip()
    success, message = restore_latest_backup()
    total_orders, total_revenue = get_sales_summary()

    return render_template(
        "employee_dashboard.html",
        employee_name=employee_name if employee_name else session.get("employee_name", "Store Employee"),
        books=get_books(),
        restock_message=message,
        total_orders=total_orders,
        total_revenue=total_revenue,
    )


if __name__ == "__main__":
    ensure_data_file()
    ensure_sales_log_file()
    ensure_vendor_orders_file()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)