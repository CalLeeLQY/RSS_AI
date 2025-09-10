### RSS_AI 部署与使用说明

一个用于批量读取 RSS 源并输出摘要到终端的简易工具。当前示例脚本默认展示每个源的前 5 条最新内容（可按需修改）。

---

## 功能概览
- 读取多个 RSS 源，解析基础信息与文章条目
- 终端打印摘要信息（可自定义过滤与展示逻辑）
- 附带一份微信/媒体 RSS 源清单 `source/channels.json`（当前脚本未自动读取）
- 预留前端目录 `rss-frontend/`（当前为空，后续可接入 Web UI）

---

## 目录结构
```text
RSS_AI/
  ├─ rss_get.py                 # 主脚本：读取与打印 RSS 摘要
  ├─ source/
  │   └─ channels.json          # RSS 源清单（示例数据，脚本未直接使用）
  ├─ rss-frontend/              # 预留前端目录（当前空）
  └─ venv/                      # 可选：本地虚拟环境目录（建议本地创建，不建议提交）
```

---

## 环境要求
- Python 3.10+（建议 3.10）
- macOS / Linux / Windows 均可（示例命令以 macOS/Linux 为主）
- 网络可访问目标 RSS 源（部分源在国内可能需要代理）

---

## 本地快速开始
1) 克隆代码（或将本目录放置到任意路径）
```bash
cd /path/to
# git clone <your-repo-url> RSS_AI
cd RSS_AI
```

2) 创建与激活虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate
python -V   # 确认版本
```

3) 安装依赖
```bash
pip install -U pip
pip install feedparser requests
```

4) 运行
```bash
python rss_get.py
```
运行后将依次读取 `rss_get.py` 中定义的各 RSS 源并打印摘要。

---

## 配置与自定义
- 选择分类：在 `rss_get.py` 末尾处，有 `test_categories` 字典与 `selected_category` 变量。
  - 将 `selected_category` 修改为你希望测试的分类，例如：`"人工智能"`、`"中文科技媒体"`、`"新闻"` 等。
- 新增 RSS 源：在相应的分类字典中追加 `名称: 链接` 键值对即可。
- 展示逻辑：默认展示每个源的前 5 条最新内容。你可以通过 `print_rss_summary(rss_data, target_day=None, max_items=5)` 调整：
  - `target_day`: 可选，按日期日号（1-31）过滤；`None` 表示不过滤。
  - `max_items`: 可选，控制每源显示条数；`None` 或不传表示默认 5。

示例：
```python
# 不按日期过滤，显示每源前 5 条（默认行为）
print_rss_summary(rss_data)

# 仅显示发布日期为 9 号的前 10 条
print_rss_summary(rss_data, target_day=9, max_items=10)

# 不按日期过滤，仅显示前 3 条
print_rss_summary(rss_data, max_items=3)
```

---

## 使用 `source/channels.json`（可选）
`source/channels.json` 提供了大量示例 RSS 源（多为微信/媒体渠道），目前脚本未自动读取。你可以手动将其中 `Links` 字段复制到 `rss_get.py` 的分类字典中使用，或按需扩展脚本读取该文件。

以下给出一个最小示例（仅用于参考，非必须修改）：
```python
# 示例：从 channels.json 读取 Links 列表并作为一个临时类别使用
import json
from pathlib import Path

with open(Path('source') / 'channels.json', 'r', encoding='utf-8') as f:
    channels = json.load(f)
links = {item['Title']: item['Links'] for item in channels[:20]}  # 仅取前20个以免过多请求

for name, url in links.items():
    print(f"\n正在读取 {name}: {url}")
    rss_data = get_rss_content(url)
    print_rss_summary(rss_data)
```

---

## Docker 部署（可选）
1) 新建 `Dockerfile`（位于项目根目录 `RSS_AI/`）：
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY rss_get.py /app/
COPY source /app/source
RUN pip install --no-cache-dir feedparser requests
CMD ["python", "rss_get.py"]
```

2) 构建镜像
```bash
docker build -t rss-ai:latest .
```

3) 运行容器
```bash
docker run --rm -it \
  -e TZ=Asia/Shanghai \
  rss-ai:latest
```
如需挂载自定义 `source/` 或输出日志，可加 `-v` 与重定向。

---

## 定时任务（可选）
- macOS/Linux 使用 cron 示例：每天 09:00 运行一次并追加到日志
```bash
crontab -e
# 添加一行（将路径替换为你的实际路径）
0 9 * * * cd /Users/<你的用户名>/Desktop/RSS_AI && /Users/<你的用户名>/Desktop/RSS_AI/venv/bin/python rss_get.py >> /Users/<你的用户名>/Desktop/RSS_AI/logs/`date +\%Y\%m\%d`.log 2>&1
```
- Windows 可使用「任务计划程序」，或通过 `schtasks` 创建计划任务。

---

## 常见问题
- 解析告警（bozo）或个别源报错：
  - 脚本会输出警告但尽量继续解析；部分源本身格式不规范或有时效性问题。
- 证书/SSL 问题：
  - 执行 `pip install certifi` 并确保系统时间正确；必要时配置网络代理。
- 国内网络访问：
  - 部分源（如 `wechat2rss` 或海外站点）在国内可能需要代理。
- 字符显示问题（Windows）：
  - 终端设置为 UTF-8（如 `chcp 65001`），或在 IDE 终端中运行。

---

## 前端说明
- `rss-frontend/` 目录为后续 Web 界面预留，当前为空，不影响后端脚本运行。
- 计划可选技术栈：React/Next.js 或简单静态页，消费由后端生成的数据。

---

## 免责声明
本项目的示例 RSS 源链接仅用于技术演示。请遵守各数据源的使用条款与版权要求，合理合规地抓取与使用数据。
