# 客服数据助手 Agent

基于 LangGraph + DeepSeek + SQLite 的电商客服数据 Agent，
通过自然语言查询订单、客户、销售、库存，并能申请退款和发送提醒。

## 技术栈

Python 3.12 / LangGraph / DeepSeek Chat API / SQLite / requests

## 核心能力

- 7 个数据库工具：订单、客户订单、销售额、库存、退款状态、退款申请、提醒
- LangGraph 状态管理与 MemorySaver 会话记忆
- 危险操作人工确认（y/n）
- 查询失败时明确拒绝编造

## 架构

START -> agent -> route
route 有工具调用 -> tools -> agent
route 无工具调用 -> END

## 运行

python create_sample_db.py
python agent.py

## 演示问题

订单 1001 现在是什么状态？
张三最近买了什么？
2026-08-30 的销售额是多少？
给经理发一条提醒，内容是订单 1001 已支付
为订单 1001 申请退款，理由写“商品破损”
查一下订单 9999

## 验证结果

- 订单 9999 返回“不存在”，不编造
- 提醒输入 n 后数据库无记录
- 退款输入 y 后 refund_requests 新增 pending 记录
