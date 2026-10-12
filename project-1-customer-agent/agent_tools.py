import db_tools

TOOL_SCHEMAS = [
    {
        "name": "get_order",
        "description": "根据订单号查询订单详情、关联客户、金额和状态",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单号，例如 1001"}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "list_orders_by_customer",
        "description": "按客户姓名查询该客户的所有订单",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "客户姓名，例如 张三"}
            },
            "required": ["customer_name"],
        },
    },
    {
        "name": "get_sales_total",
        "description": "查询某一天的销售额和订单数量",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "日期，格式 YYYY-MM-DD，例如 2026-08-30"}
            },
            "required": ["date"],
        },
    },
    {
        "name": "get_product_stock",
        "description": "按商品名称查询库存和价格",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string", "description": "商品名称，例如 机械键盘"}
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "get_refund_status",
        "description": "查询某订单的退款申请状态",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单号"}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "send_reminder",
        "description": "给某人发送提醒，属于有副作用的操作",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string", "description": "接收人，例如 经理"},
                "message": {"type": "string", "description": "提醒内容"}
            },
            "required": ["recipient", "message"],
        },
    },
    {
        "name": "apply_refund",
        "description": "为某订单提交退款申请，属于有副作用的操作",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "订单号"},
                "reason": {"type": "string", "description": "退款原因"}
            },
            "required": ["order_id", "reason"],
        },
    },
]

TOOLS = [
    {"type": "function", "function": schema}
    for schema in TOOL_SCHEMAS
]

TOOL_FUNCTIONS = {
    "get_order": db_tools.get_order,
    "list_orders_by_customer": db_tools.list_orders_by_customer,
    "get_sales_total": db_tools.get_sales_total,
    "get_product_stock": db_tools.get_product_stock,
    "get_refund_status": db_tools.get_refund_status,
    "send_reminder": db_tools.send_reminder,
    "apply_refund": db_tools.apply_refund,
}

RISKY_TOOLS = {"send_reminder", "apply_refund"}


def execute_tool(name: str, args: dict) -> dict:
    func = TOOL_FUNCTIONS.get(name)

    if func is None:
        return {"error": f"未知工具：{name}"}

    if name in RISKY_TOOLS:
        answer = input(f"是否执行 {name}，参数：{args}？(y/n) ")
        if answer.strip().lower() not in ("y", "yes"):
            return {"status": "blocked", "reason": "用户未批准", "tool": name}

    try:
        return func(**args)
    except Exception as exc:
        return {"error": f"{name} 执行失败：{exc}"}