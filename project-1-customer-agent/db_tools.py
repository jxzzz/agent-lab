import datetime
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "support.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def rows_to_dicts(rows) -> list:
    return [dict(row) for row in rows]


def get_order(order_id: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT o.id,
                   o.customer_id,
                   c.name AS customer_name,
                   c.level AS customer_level,
                   o.product,
                   o.amount,
                   o.status,
                   o.created_at
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            WHERE o.id = ?
            """,
            (order_id,),
        ).fetchone()

        if row is None:
            return {"error": f"订单 {order_id} 不存在"}
        return dict(row)
    finally:
        conn.close()


def list_orders_by_customer(customer_name: str) -> dict:
    conn = get_connection()
    try:
        customer = conn.execute(
            "SELECT id, name FROM customers WHERE name = ?",
            (customer_name,),
        ).fetchone()

        if customer is None:
            return {"error": f"客户 {customer_name} 不存在"}

        rows = conn.execute(
            """
            SELECT o.id, o.product, o.amount, o.status, o.created_at
            FROM orders o
            JOIN customers c ON c.id = o.customer_id
            WHERE c.name = ?
            ORDER BY o.created_at DESC
            """,
            (customer_name,),
        ).fetchall()

        return {"customer": customer_name, "orders": rows_to_dicts(rows)}
    finally:
        conn.close()


def get_sales_total(date: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT COUNT(*) AS order_count, COALESCE(SUM(amount), 0) AS total
            FROM orders
            WHERE substr(created_at, 1, 10) = ?
            """,
            (date,),
        ).fetchone()

        result = dict(row)
        return {
            "date": date,
            "order_count": result["order_count"],
            "total": result["total"],
        }
    finally:
        conn.close()


def get_product_stock(product_name: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, name, stock, price FROM products WHERE name = ?",
            (product_name,),
        ).fetchone()

        if row is None:
            return {"error": f"商品 {product_name} 不存在"}
        return dict(row)
    finally:
        conn.close()


def get_refund_status(order_id: str) -> dict:
    conn = get_connection()
    try:
        row = conn.execute(
            """
            SELECT id, status, reason, created_at
            FROM refund_requests
            WHERE order_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (order_id,),
        ).fetchone()

        if row is None:
            return {"error": f"订单 {order_id} 没有退款申请"}
        return dict(row)
    finally:
        conn.close()


def apply_refund(order_id: str, reason: str) -> dict:
    order = get_order(order_id)
    if "error" in order:
        return order

    conn = get_connection()
    try:
        existing = conn.execute(
            """
            SELECT id FROM refund_requests
            WHERE order_id = ? AND status = 'pending'
            """,
            (order_id,),
        ).fetchone()

        if existing is not None:
            return {"error": f"订单 {order_id} 已有待处理的退款申请"}

        created_at = datetime.datetime.now().isoformat(timespec="seconds")
        cur = conn.execute(
            """
            INSERT INTO refund_requests (order_id, reason, status, created_at)
            VALUES (?, ?, 'pending', ?)
            """,
            (order_id, reason, created_at),
        )
        conn.commit()
        return {
            "status": "created",
            "refund_request_id": cur.lastrowid,
            "order_id": order_id,
            "reason": reason,
        }
    finally:
        conn.close()


def send_reminder(recipient: str, message: str) -> dict:
    conn = get_connection()
    try:
        created_at = datetime.datetime.now().isoformat(timespec="seconds")
        cur = conn.execute(
            """
            INSERT INTO reminders (recipient, message, status, created_at)
            VALUES (?, ?, 'sent', ?)
            """,
            (recipient, message, created_at),
        )
        conn.commit()
        return {
            "status": "sent",
            "reminder_id": cur.lastrowid,
            "recipient": recipient,
            "message": message,
        }
    finally:
        conn.close()