Excellent. This is one of the most important documents in the project because **every API, every SQL query, every dashboard, and every automation will use these tables.**

I also want to change **how** we create this document.

Instead of me giving you a finished database design, I'll act like a **Senior Database Architect** explaining every decision. By the end, you'll know *why* every table exists, not just what columns it has.

---

# DATABASE_DESIGN.md

# SpiceFlow – Database Design Document

Version: 1.0

Status: Draft

---

# 1. Purpose

## 1.1 Overview

This document describes the database design for the SpiceFlow platform.

The database is responsible for storing, organizing, and managing all business information required for the daily operation of the organic spice business.

The design follows the principles of **normalization**, **data integrity**, **scalability**, and **maintainability** to ensure the application can support future business growth without requiring major structural changes.

---

# 2. Database Technology

| Property   | Value      |
| ---------- | ---------- |
| Database   | PostgreSQL |
| ORM        | SQLAlchemy |
| Validation | Pydantic   |
| Backend    | FastAPI    |

---

# 3. Database Design Principles

The database has been designed according to the following principles:

### Data Integrity

Every record should remain accurate and consistent.

Example:

* Orders cannot exist without customers.
* Payments cannot exist without orders.

---

### Normalization

Information should be stored only once whenever possible.

Instead of writing the customer's address inside every order,

Store

Customer

↓

Address

↓

Order references Address.

This reduces duplication.

---

### Scalability

The database should support

* More products
* More customers
* Multiple warehouses (future)
* More employees
* More campaigns

without redesign.

---

### Security

Sensitive information like passwords will never be stored as plain text.

Only password hashes are stored.

---

# 4. Entity List

The following entities represent the core business objects.

| Entity        | Purpose                  |
| ------------- | ------------------------ |
| Users         | Stores all system users  |
| Roles         | Defines user permissions |
| Addresses     | Customer addresses       |
| Categories    | Product categories       |
| Products      | Organic spice products   |
| Inventory     | Product stock            |
| Cart          | Shopping cart            |
| Cart Items    | Products inside cart     |
| Orders        | Customer orders          |
| Order Items   | Products inside order    |
| Payments      | Payment information      |
| Deliveries    | Delivery tracking        |
| Employees     | Employee information     |
| Coupons       | Discount coupons         |
| Rewards       | Loyalty rewards          |
| QR Campaigns  | Marketing campaigns      |
| Reviews       | Product reviews          |
| Notifications | System notifications     |

---

# 5. Entity Descriptions

---

## Users

Purpose

Stores every person who uses the system.

Includes

* Owner
* Employees
* Delivery Staff
* Customers

---

Suggested Attributes

| Field         | Description        |
| ------------- | ------------------ |
| id            | Primary Key        |
| first_name    | User's first name  |
| last_name     | User's last name   |
| email         | Unique email       |
| phone         | Contact number     |
| password_hash | Encrypted password |
| role_id       | User role          |
| created_at    | Registration date  |
| updated_at    | Last update        |

---

## Roles

Purpose

Defines access permissions.

Example roles

* Owner
* Employee
* Delivery
* Customer

Attributes

| Field     | Description |
| --------- | ----------- |
| id        | Primary Key |
| role_name | Role name   |

---

## Products

Purpose

Stores product information.

Example

Organic Turmeric Powder

Attributes

| Field       | Description         |
| ----------- | ------------------- |
| id          | Primary Key         |
| category_id | Product category    |
| sku         | Product SKU         |
| name        | Product name        |
| description | Product description |
| weight      | Product weight      |
| price       | Selling price       |
| image_url   | Product image       |
| status      | Active / Inactive   |
| created_at  | Creation date       |

---

## Categories

Purpose

Groups similar products.

Examples

* Turmeric
* Chilli
* Coriander

Attributes

| Field         | Description |
| ------------- | ----------- |
| id            | Primary Key |
| category_name | Category    |
| description   | Description |

---

## Inventory

Purpose

Tracks stock.

Attributes

| Field         | Description       |
| ------------- | ----------------- |
| id            | Primary Key       |
| product_id    | Product           |
| quantity      | Available stock   |
| minimum_stock | Alert level       |
| last_updated  | Last stock update |

---

## Cart

Purpose

Represents one customer's shopping cart.

Attributes

* id
* customer_id
* created_at

---

## Cart Items

Purpose

Stores products added to the cart.

Attributes

* id
* cart_id
* product_id
* quantity

---

## Orders

Purpose

Stores customer orders.

Attributes

| Field          | Description                      |
| -------------- | -------------------------------- |
| id             | Primary Key                      |
| order_number   | Unique order number              |
| customer_id    | Customer                         |
| address_id     | Delivery address                 |
| payment_status | Paid / Pending                   |
| order_status   | Processing / Shipped / Delivered |
| total_amount   | Total order value                |
| created_at     | Order date                       |

---

## Order Items

Purpose

Stores products belonging to an order.

Attributes

* id
* order_id
* product_id
* quantity
* unit_price
* subtotal

---

## Payments

Purpose

Stores payment details.

Attributes

* id
* order_id
* payment_method
* transaction_id
* amount
* payment_status
* payment_date

---

## Deliveries

Purpose

Tracks delivery.

Attributes

* id
* order_id
* delivery_person_id
* status
* delivery_date

---

## Reviews

Purpose

Customer feedback.

Attributes

* id
* customer_id
* product_id
* rating
* review
* created_at

---

## Coupons

Purpose

Discount campaigns.

Attributes

* id
* coupon_code
* discount
* expiry_date
* status

---

## Rewards

Purpose

Customer loyalty.

Attributes

* id
* customer_id
* points
* reward_level

---

## QR Campaigns

Purpose

Stores marketing campaigns.

Attributes

* id
* campaign_name
* qr_code
* start_date
* end_date

---

## Notifications

Purpose

Stores notifications.

Attributes

* id
* user_id
* title
* message
* notification_type
* status
* created_at

---

# 6. Entity Relationships

| Relationship                          | Type |
| ------------------------------------- | ---- |
| One Role → Many Users                 | 1:N  |
| One Customer → Many Addresses         | 1:N  |
| One Customer → Many Orders            | 1:N  |
| One Order → Many Order Items          | 1:N  |
| One Product → Many Order Items        | 1:N  |
| One Category → Many Products          | 1:N  |
| One Product → One Inventory           | 1:1  |
| One Customer → One Cart               | 1:1  |
| One Cart → Many Cart Items            | 1:N  |
| One Product → Many Cart Items         | 1:N  |
| One Order → One Payment               | 1:1  |
| One Delivery Person → Many Deliveries | 1:N  |
| One Product → Many Reviews            | 1:N  |
| One Customer → Many Reviews           | 1:N  |

---

# 7. ER Diagram (High-Level)

```text
                    Roles
                      │
                 (1)  │  (N)
                      ▼
                    Users
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   Addresses       Orders      Notifications
                      │
                 (1)  │  (N)
                      ▼
                 Order Items
                ▲           ▲
                │           │
                │           │
           Products ─── Inventory
                │
                ▼
            Categories

Users
   │
   ▼
 Cart
   │
   ▼
Cart Items
```

---

# 8. Naming Conventions

* Table names use **plural nouns** (`users`, `products`, `orders`).
* Primary keys use `id`.
* Foreign keys use `<table>_id` (for example, `user_id`, `product_id`).
* Timestamp fields use `created_at` and `updated_at`.
* Boolean fields start with `is_` (for example, `is_active`).

---

# 9. Constraints

* Email addresses must be unique.
* Product SKUs must be unique.
* Coupon codes must be unique.
* Ratings must be between **1** and **5**.
* Product prices cannot be negative.
* Inventory quantities cannot be negative.
* Every order must belong to a valid customer.
* Every payment must belong to a valid order.

---

# 10. Future Database Expansion

The schema has been designed to accommodate future features without major restructuring, including:

* Supplier Management
* Purchase Orders
* Warehouses
* Inventory Transfers
* Franchise Management
* Multi-vendor Support
* Subscription Orders
* AI Recommendation History
* Customer Behavior Analytics
* Voice Order Logs
* Marketing Performance Metrics

**I would *not* finalize this database yet.**

Why?
Because right now it's a **business-level database design**, not an **implementation-level database design**.
