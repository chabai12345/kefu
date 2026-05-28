# 电商客服系统 (E-Commerce Customer Service System)

基于 LLM 的智能电商客服系统，支持多意图识别、知识库检索（RAG）、订单管理、联网搜索等功能。

## 功能特性

- **智能对话** — 基于 LLM 的意图识别与多轮对话，支持问候、订单查询、售后政策、退换货等常见场景
- **快速意图匹配** — 关键词规则引擎直接匹配常见意图，无需 LLM 调用，响应时间 < 0.1s
- **多意图处理** — 支持单条消息中包含多个意图（如"我要退货顺便查一下其他订单"）
- **RAG 知识库检索** — 连接 MCP Server 检索售后政策、商品信息等内部知识
- **订单管理** — REST API 完成订单的创建、查询、更新、删除，支持分页和筛选
- **订单导入适配器** — 抽象接口设计，预留淘宝、京东等外部平台接入能力
- **WebSocket 实时通信** — 前端实时聊天界面，支持打字指示器
- **快捷操作面板** — 预设快捷按钮（查订单、商品咨询、售后政策、退换货）

## 架构

```
┌─────────────┐     WebSocket      ┌──────────────────┐
│  Frontend    │ ◄──────────────►  │     Backend       │
│  (React+TS)  │                    │  (FastAPI+Python)  │
└─────────────┘                    └──────────────────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼            ▼            ▼
                      ┌──────────┐ ┌──────────┐ ┌──────────┐
                      │ Intent    │ │  Agent    │ │  Order   │
                      │ Classifier│ │ Executor  │ │  CRUD    │
                      └──────────┘ └──────────┘ └──────────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼            ▼            ▼
                      ┌──────────┐ ┌──────────┐ ┌──────────┐
                      │  RAG     │ │  Order   │ │  Order   │
                      │  MCP     │ │  Service │ │  Import  │
                      └──────────┘ └──────────┘ └──────────┘
```

### 核心模块

| 模块 | 说明 |
|------|------|
| `engine/intent_classifier.py` | 意图分类器：关键词规则 + LLM 分类，支持 14 种常见意图 |
| `engine/router.py` | 意图路由：根据分类结果分发到对应处理逻辑 |
| `engine/agent.py` | Agent 执行器：LLM Function Calling 动态调用工具 |
| `engine/context_manager.py` | 会话管理：多轮对话上下文维护 |
| `api/ws_handler.py` | WebSocket 聊天接口 |
| `api/order_routes.py` | 订单 REST API（POST/GET/PUT/DELETE）|
| `tools/tool_definitions.py` | LLM 工具定义（查询知识库、订单操作、搜索等 10 个工具）|
| `tools/order_service.py` | 订单数据库操作层 |
| `tools/order_import/` | 订单导入适配器接口（预留淘宝等平台对接）|
| `tools/rag_client.py` | RAG MCP Server 客户端 |
| `tools/rag_generator.py` | RAG 结果生成 |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- （可选）RAG MCP Server

### 后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
.venv\Scripts\activate        # Windows

pip install -r requirements.txt
cp .env.example .env          # 配置 LLM API Key

# 初始化数据库
python scripts/init_db.py

# 启动服务
python app.py
```

后端默认运行在 `http://localhost:8001`。

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`，支持 WebSocket 连接后端。

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_API_KEY` | — | LLM API 密钥 |
| `LLM_BASE_URL` | `https://api.deepseek.com` | LLM API 地址 |
| `LLM_MODEL` | `deepseek-chat` | LLM 模型名称 |
| `EMBEDDING_API_KEY` | — | Embedding API 密钥 |
| `EMBEDDING_BASE_URL` | `https://api.siliconflow.cn/v1` | Embedding API 地址 |
| `EMBEDDING_MODEL` | `BAAI/bge-large-zh-v1.5` | Embedding 模型 |
| `RAG_MCP_URL` | `http://localhost:8000` | RAG MCP 服务地址 |
| `PORT` | `8001` | 服务端口 |

## API 文档

### REST API

**订单管理** — `http://localhost:8001/api/v1/orders`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/orders` | 创建订单 |
| GET | `/api/v1/orders` | 订单列表（支持 page, page_size, status, source, keyword 参数）|
| GET | `/api/v1/orders/{order_id}` | 订单详情 |
| PUT | `/api/v1/orders/{order_id}` | 更新订单 |
| DELETE | `/api/v1/orders/{order_id}` | 取消订单 |

### WebSocket

`ws://localhost:8001/ws` — 客服聊天 WebSocket 接口。

消息格式：

```json
{
  "type": "message",
  "session_id": "uuid",
  "message": "用户消息"
}
```

响应格式：

```json
{
  "type": "reply",
  "session_id": "uuid",
  "reply": "客服回复",
  "intents": [...],
  "suggest_human": false
}
```

## 意图分类

系统支持 14 种意图，通过关键词规则优先匹配（0.1s），未命中则 fallback 到 LLM 分类：

| 意图 | 触发关键词 |
|------|-----------|
| greeting | 你好、您好、嗨、hi、hello、在吗 |
| order_status | 查订单、我的订单、订单列表 |
| human_handoff | 转人工、人工客服 |
| after_sale_policy | 售后政策、保修、售后 |
| return_request | 退货、退换货 |
| refund_inquiry | 退款 |
| exchange_request | 换货 |
| order_cancel | 取消订单 |
| order_modify | 修改订单 |
| order_confirm | 确认收货 |
| delivery_inquiry | 物流、快递、发货 |
| recommendation | 推荐商品 |
| price_inquiry | 价格、多少钱 |
| farewell | 再见、谢谢、拜拜 |

## 项目结构

```
ecommerce-cs/
├── backend/
│   ├── api/                  # FastAPI 路由（REST + WebSocket）
│   ├── config/               # 配置
│   ├── engine/               # 核心引擎（分类器、路由、Agent、会话管理）
│   ├── models/               # 数据模型（SQLAlchemy + Pydantic）
│   ├── prompts/              # LLM 提示词模板
│   ├── scripts/              # 工具脚本
│   └── tools/                # 工具层（知识库、订单服务、导入适配器）
├── frontend/
│   └── src/
│       ├── components/       # React 组件
│       ├── hooks/            # 自定义 Hooks
│       └── types/            # TypeScript 类型定义
└── docs/                     # 文档
```
