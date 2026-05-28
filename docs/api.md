# 电商客服系统 API 文档

## 基础信息

- Base URL: `http://localhost:8001/api/v1`
- WebSocket: `ws://localhost:8001/api/v1/ws`

## REST 接口

### 健康检查
```
GET /api/v1/health
Response: {"status": "ok", "service": "ecommerce-cs"}
```

### 发送消息 (REST)
```
POST /api/v1/chat
Body: {
  "session_id": "string",
  "message": "string",
  "platform": "web"
}
Response: {
  "session_id": "string",
  "reply": "string",
  "intents": [...],
  "rich_data": {...} | null,
  "suggest_human": bool
}
```

### 获取历史
```
GET /api/v1/sessions/{session_id}/history?limit=10
Response: {
  "session_id": "string",
  "messages": [...]
}
```

## WebSocket

### 连接
```
ws://localhost:8001/api/v1/ws
```

### 发送
```json
{"message": "iPhone 15多少钱"}
```

### 接收
```json
{
  "session_id": "ws_xxx",
  "reply": "iPhone 15 目前售价 5999 元起",
  "intents": [{"id": 1, "intent": "price_inquiry", "params": {"product": "iPhone 15"}, "confidence": 0.95}],
  "rich_data": null,
  "suggest_human": false
}
```

## 多端接入

### 微信接入
将消息转发到 `POST /api/v1/chat` 即可。

### App 接入
使用 WebSocket 或 REST 接口均可。

### CLI 接入
```bash
curl -X POST http://localhost:8001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "cli-1", "message": "我的订单到哪了"}'
```
