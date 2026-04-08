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
    return render_template(
        "employee_dashboard.html",
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

    return render_template(
        "employee_dashboard.html",
        employee_name=employee_name if employee_name else session.get("employee_name", "Store Employee"),
        books=get_books(),
        restock_message=restock_message,
    )


@app.route("/restore-backup", methods=["POST"])
def restore_backup():
    employee_name = request.form.get("employee_name", "").strip()
    success, message = restore_latest_backup()

    return render_template(
        "employee_dashboard.html",
        employee_name=employee_name if employee_name else session.get("employee_name", "Store Employee"),
        books=get_books(),
        restock_message=message,
    )


if __name__ == "__main__":
    ensure_data_file()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
