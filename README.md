# ai-app-bots
自动化爬取 ai-apps，分析 ai-apps，提取 ai-app 中 chat 功能的解码器。

## Discovery Bot
参考 Aurascape 的 AI 应用发现思路，实现一个轻量级 discovery bot。它通过抓取网页内容，提取元信息与文本样本，结合关键词启发式完成：

- AI 应用识别与置信度估计
- 应用类型分类（chat / image / audio / video / code 等）
- chat 能力识别与解码器类型推断（SSE / WebSocket / polling）
- 可能的 API 端点提取

### 使用方式
直接扫描单个 URL：

```bash
python -m discovery_bot --url https://example.com --output discovery_results.json
```

从文件读取多个 URL（每行一个，支持 `#` 注释）：

```bash
python -m discovery_bot --input urls.txt --format jsonl --output discovery_results.jsonl
```

常用参数：

- `--timeout` 请求超时时间（秒）
- `--max-workers` 并发抓取线程数
- `--max-bytes` 单页最大读取字节数
- `--limit` 限制处理的 URL 数量

### 输出字段说明
输出为 JSON / JSONL，包含：

- `metadata`：title、description、og 元信息、language、text_sample
- `is_ai_app` / `confidence`：AI 应用判断与置信度
- `categories`：识别到的应用类别
- `chat_capability` / `chat_decoder`：chat 能力与解码器推断
- `endpoints`：页面中提取到的 API 端点
- `errors`：抓取或解析错误信息
