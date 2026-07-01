# Pacific Times Book Market - Database Schema

## Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ CART : has
    USER ||--o{ ORDER : places
    USER ||--o{ "PAYMENT" : makes
    CART ||--o{ CARTITEM : contains
    CARTITEM }o--|| BOOK : adds_to
    ORDER ||--o{ "ORDERITEM" : contains
    "ORDERITEM" }o--|| BOOK : includes
    BOOK }o--|| AUTHOR : "written by"

    USER {
        int user_id PK
        string first_name
        string last_name
        string email UK
        string password
        string phone_number
        string role "customer or admin"
    }

    CART {
        int cart_id PK
        int user_id FK
        string cart_status
    }

    CARTITEM {
        int cart_item_id PK
        int cart_id FK
        int book_id FK
        int quantity
        float unit_price
    }

    ORDER {
        int order_id PK
        int user_id FK
        string order_date
        string shipping_address_id FK
        string billing_address_id FK
        float subtotal
        float tax
        float shipping_fee
        float total_amount
    }

    "ORDERITEM" {
        int order_item_id PK
        int order_id FK
        int book_id FK
        int quantity
        float unit_price
        float line_total
    }

    "PAYMENT" {
        int payment_id PK
        int order_id FK
        string payment_method
        string paid_at
    }

    BOOK {
        int book_id PK
        string title UK
        int author_id FK
        string category
        string ISBN UK
        float price
        int stock_qty
    }

    AUTHOR {
        int author_id PK
        string book_id FK
        string author_id FK
    }
```

## Tables Overview

### USER
- **user_id** (PK): Unique identifier
- **first_name**: Customer/admin first name
- **last_name**: Customer/admin last name
- **email** (UK): Unique email address
- **password**: Encrypted password
- **phone_number**: Contact number
- **role**: "customer" or "admin"

### CART
- **cart_id** (PK): Unique identifier
- **user_id** (FK): References USER
- **cart_status**: Current status

### CARTITEM
- **cart_item_id** (PK): Unique identifier
- **cart_id** (FK): References CART
- **book_id** (FK): References BOOK
- **quantity**: Number of items
- **unit_price**: Price per unit

### ORDER
- **order_id** (PK): Unique identifier
- **user_id** (FK): References USER
- **order_date**: When order was placed
- **shipping_address_id** (FK): Shipping location
- **billing_address_id** (FK): Billing location
- **subtotal**: Sum before tax/shipping
- **tax**: Tax amount
- **shipping_fee**: Shipping cost
- **total_amount**: Final total

### ORDERITEM
- **order_item_id** (PK): Unique identifier
- **order_id** (FK): References ORDER
- **book_id** (FK): References BOOK
- **quantity**: Number ordered
- **unit_price**: Price at time of order
- **line_total**: quantity × unit_price

### PAYMENT
- **payment_id** (PK): Unique identifier
- **order_id** (FK): References ORDER
- **payment_method**: Credit card, PayPal, etc.
- **paid_at**: Payment timestamp

### BOOK
- **book_id** (PK): Unique identifier
- **title** (UK): Book title
- **author_id** (FK): References AUTHOR
- **category**: Book genre/category
- **ISBN** (UK): Unique book code
- **price**: Current price
- **stock_qty**: Available inventory

### AUTHOR
- **author_id** (PK): Unique identifier
- **book_id** (FK): References BOOK
- **author_id** (FK): References AUTHOR

## Relationships

| From | To | Type | Description |
|------|----|----|-------------|
| USER | CART | 1:M | One user has many carts |
| USER | ORDER | 1:M | One user places many orders |
| USER | PAYMENT | 1:M | One user makes many payments |
| CART | CARTITEM | 1:M | One cart contains many items |
| CARTITEM | BOOK | M:1 | Many cart items reference books |
| ORDER | ORDERITEM | 1:M | One order contains many items |
| ORDERITEM | BOOK | M:1 | Many order items reference books |
| BOOK | AUTHOR | M:1 | Many books written by one author |

---

**Legend:**
- **PK**: Primary Key
- **FK**: Foreign Key
- **UK**: Unique Key
- **1:M**: One-to-Many relationship
- **M:1**: Many-to-One relationship
