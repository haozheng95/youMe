下面是针对上述 Flask 应用中活动（Activity）的增删改查（CRUD）操作的 `curl` 测试命令：

### 创建活动 (POST /activities)

```bash
curl -X POST http://localhost:5000/activities -H "Content-Type: application/json" -d '  
{  
    "name": "Example Activity",  
    "description": "This is an example activity description.",  
    "address": "123 Main Street, Cityville",  
    "start_date": "2023-04-01 10:00:00",  
    "end_date": "2023-04-01 14:00:00",  
    "minimum_number_of_participants": 5,  
    "maximum_number_of_participants": 20,  
    "price": 50,  
    "date": "2023-04-01 10:00:00",  
    "date": "2023-04-01 10:00:00", 
    "img_link": "https://hssx.top/static/assets/img/demo/blog6.jpg",
    "banner": 0 ,
    "activity_type": 1
}'
```

### 获取所有活动 (GET /activities)

```bash
curl -X GET http://localhost:5000/activities
```

### 获取单个活动 (GET /activities/<int:activity_id>)

假设你想获取 ID 为 1 的活动：

```bash
curl -X GET http://localhost:5000/activities/1
```

### 更新活动 (PUT /activities/<int:activity_id>)

假设你想更新 ID 为 1 的活动的名称：

```bash
curl -X PUT -H "Content-Type: application/json" -d '{"name": "Updated Activity Name", "date": "2023-03-16 10:00:00"}' http://localhost:5000/activities/1
```

### 删除活动 (DELETE /activities/<int:activity_id>)

假设你想删除 ID 为 1 的活动：

```bash
curl -X DELETE http://localhost:5000/activities/1
```

这些 `curl` 命令假设 Flask 应用正在本地主机的 5000 端口上运行。你需要根据实际情况替换 URL 中的端口号，如果 Flask
应用配置了不同的端口。

请注意，对于 `POST`、`PUT` 请求，我们使用了 `-d` 参数来发送 JSON 格式的请求体。同时，对于所有的请求，我们可能需要根据 Flask
应用是否启用了认证和授权机制来添加相应的 HTTP 头部，比如 `Authorization` 头部来包含认证令牌。

此外，请确保 `curl` 命令中的 JSON 数据格式与 Flask
应用期望的格式相匹配，包括字段名称和日期格式等。在上述示例中，我们假设活动名称是 `name`，日期是 `date`
，并且日期格式为 `YYYY-MM-DD HH:MM:SS`。如果 Flask 应用中定义的字段或格式不同，请相应地调整 `curl` 命令中的 JSON 数据。
