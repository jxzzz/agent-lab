import random
import sqlite3
from pathlib import Path
import datetime

DB_PATH = Path(__file__).parent / "support.db"

customers = [
    ("C001", "张三", "普通客户"),
    ("C002", "李四", "会员"),
    ("C003", "王五", "普通客户"),
    ("C004", "赵六", "VIP"),
    ("C005", "钱七", "会员"),
    ("C006", "孙八", "普通客户"),
]

products = [
    ("P001", "无线鼠标", 200, 79),
    ("P002", "机械键盘", 150, 299),
    ("P003", "显示器", 80, 1299),
    ("P004", "USB-C 数据线", 500, 39),
    ("P005", "笔记本支架", 300, 129),
    ("P006", "降噪耳机", 60, 899),
    ("P007", "便携充电宝", 250, 149),
    ("P008", "高清摄像头", 90, 399),
    ("P009", "桌面音箱", 120, 459),
    ("P010", "电脑背包", 180, 219),
]

random.seed(42)
orders = []
for i in range(1, 21):
    customer_id, _, _ = random.choice(customers)
    product_id, product_name, _, price = random.choice(products)
    status = random.choices(
        ["已支付", "已发货", "已签收"],
        weights=[3, 3, 4],
    )[0]
    seed_date = datetime.date(2026, 8, 29) + datetime.timedelta(days=random.randint(0, 4))
    created_at = f"{seed_date.isoformat()} 10:00"
    orders.append((str(1000 + i), customer_id, product_name, price, status, created_at))

refund_requests = [
    ("1006", "商品收到时有划痕", "pending", "2026-08-31"),
    ("1013", "线材接触不良", "approved", "2026-09-01"),
]


def create_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS reminders;
        DROP TABLE IF EXISTS refund_requests;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            level TEXT NOT NULL
        );

        CREATE TABLE products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stock INTEGER NOT NULL,
            price REAL NOT NULL
        );

        CREATE TABLE orders (
            id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL REFERENCES customers(id),
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE refund_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL REFERENCES orders(id),
            reason TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL
        );

        CREATE TABLE reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'sent',
            created_at TEXT NOT NULL
        );
    """)

    cur.executemany(
        "INSERT INTO customers (id, name, level) VALUES (?, ?, ?)",
        customers,
    )
    cur.executemany(
        "INSERT INTO products (id, name, stock, price) VALUES (?, ?, ?, ?)",
        products,
    )
    cur.executemany(
        """
        INSERT INTO orders (id, customer_id, product, amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        orders,
    )
    cur.executemany(
        """
        INSERT INTO refund_requests (order_id, reason, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        refund_requests,
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_db()
    print("support.db 创建完成")