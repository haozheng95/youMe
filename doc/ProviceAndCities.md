在 Flask 应用中，你可以通过直接在命令行中使用 `curl` 工具来调用 API。`curl` 是一个命令行工具，用于发送 HTTP 请求并获取响应。

假设你的 Flask 应用正在本地运行，并且监听默认的 5000 端口，你可以使用以下 `curl` 命令来调用上面定义的 API 端点：

### 获取所有省份列表

```bash
curl http://127.0.0.1:5000/provinces
```

### 根据省份名称获取对应的城市列表

```bash
curl http://127.0.0.1:5000/province/广东省/cities
```

如果你想要将这些 `curl` 命令集成到你的脚本中，或者想要以编程方式生成它们，你可以使用 Python 来构建这些命令的字符串。下面是一个简单的 Python 函数，它接受一个省份名称作为参数，并生成相应的 `curl` 命令字符串：

```python
def generate_curl_command(province_name):
    base_url = "http://127.0.0.1:5000"
    cities_endpoint = f"/province/{province_name}/cities"
    curl_command = f"curl {base_url}{cities_endpoint}"
    return curl_command

# 使用示例
province_name = "广东省"
curl_cmd = generate_curl_command(province_name)
print(curl_cmd)
```

运行上面的代码将输出：

```bash
curl http://127.0.0.1:5000/province/广东省/cities
```

然后你可以复制这个命令并在命令行中执行它，或者将其集成到你的脚本中。

请注意，如果你的 Flask 应用部署在远程服务器或使用了不同的端口，你需要将 `127.0.0.1:5000` 替换为实际的服务器地址和端口。同时，如果你的 API 需要身份验证（如 API 密钥或令牌），你还需要在 `curl` 命令中包含相应的身份验证信息。
