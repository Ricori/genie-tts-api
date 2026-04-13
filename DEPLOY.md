# Modal 部署指南

## 1. 安装 Modal CLI

```bash
pip install modal
```

## 2. 登录 Modal

```bash
modal token new
```

这会打开浏览器让你登录 Modal 账号(可以用 GitHub 登录)。

## 3. 部署应用

```bash
modal deploy modal_app.py
```

部署成功后会得到一个公网 URL,类似:
```
https://your-username--genie-tts-api-fastapi-app.modal.run
```

## 4. 测试 API

```bash
curl -X POST "https://your-url.modal.run/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは"}' \
  --output test.wav
```

## 5. 查看日志

```bash
modal app logs genie-tts-api
```

## 配置说明

### CPU 配置
- `cpu=4.0`: 使用 4 核 CPU
- 可选值: 0.25, 0.5, 1.0, 2.0, 4.0, 8.0
- 推荐 4.0 以上以获得更好的推理性能

### Keep Warm
`keep_warm=1` 会保持1个实例始终运行,避免冷启动延迟。
- 设为 0: 完全按需启动(省钱但有冷启动)
- 设为 1-N: 保持 N 个实例热启动

### 内存和超时
- `memory`: 内存大小(MB)
- `timeout`: 单次请求超时时间(秒)

## 成本估算

Modal 按使用量计费:
- CPU 时间: ~$0.03/小时 (4 核 CPU)
- 存储: 免费额度足够
- 网络: 免费额度足够

`keep_warm=1` 会产生持续费用,建议开发时设为 0。

## 本地开发

```bash
modal serve modal_app.py
```

这会在本地启动服务,但使用 Modal 的 GPU 资源。
