import json
import db_tools as db

print("1. 查订单 1001")
print(json.dumps(db.get_order("1001"), ensure_ascii=False, indent=2))
print()

print("2. 查张三的订单")
print(json.dumps(db.list_orders_by_customer("张三"), ensure_ascii=False, indent=2))
print()

print("3. 查 2026-08-30 的销售额")
print(json.dumps(db.get_sales_total("2026-08-30"), ensure_ascii=False, indent=2))
print()

print("4. 查机械键盘库存")
print(json.dumps(db.get_product_stock("机械键盘"), ensure_ascii=False, indent=2))
print()

print("5. 查订单 1006 的退款状态")
print(json.dumps(db.get_refund_status("1006"), ensure_ascii=False, indent=2))
print()

print("6. 给经理发提醒")
print(json.dumps(db.send_reminder("经理", "测试提醒"), ensure_ascii=False, indent=2))
print()

print("7. 为订单 1020 申请退款")
print(json.dumps(db.apply_refund("1020", "测试退款"), ensure_ascii=False, indent=2))