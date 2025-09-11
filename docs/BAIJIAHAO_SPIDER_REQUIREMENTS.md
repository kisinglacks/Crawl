# 百家号最新文章抓取器（需求说明）

> 目标：从**已收集好的百家号作者列表**中，定期抓取各作者**最新发布**的文章，解析正文与元数据，**保存到本地**（文件与数据库二选一或同时），支持断点续抓、去重、代理与限速，支持计划任务自动运行。

---

## 1. 范围与非目标

* ✅ 范围

  * 输入：作者列表（作者主页 URL / 作者 ID）。
  * 输出：文章元数据 + 正文内容 + 资源（可选保存图片）。
  * 定时：支持 cron（如每 15 分钟/每小时）。
  * 去重：按文章唯一 ID/URL 去重。
  * 失败重试与错误日志。
* ❌ 非目标

  * 不做内容分析/摘要（可作为后续扩展）。
  * 不做反检测的强对抗策略（仅做基础限速/代理/随机 UA）。

> ⚠️ 合规提示：请遵守目标网站的服务条款与当地法律法规；仅用于学习/允许的范围内，不要用于商业化或大规模抓取。尊重 `robots.txt`（若有）。

---

## 2. 输入与输出

### 2.1 输入（作者列表）

* 文件：`data/authors.txt`（UTF-8，一行一个）

  ```
  https://author.baidu.com/home/1640549925951234
  https://author.baidu.com/home/1654321234567890
  # 支持注释行，以 # 开头
  ```
* 也可支持 `authors.csv`：`author_id,author_name,homepage_url`

### 2.2 输出（两种落地方式，可同时启用）

* **文件落地**：

  * 目录：`output/YYYYMMDD/<author_id>/<article_id>.json`
  * 正文纯文本：`output/YYYYMMDD/<author_id>/<article_id>.txt`
    -（可选）图片下载：`output/YYYYMMDD/<author_id>/images/<hash>.jpg`
* **数据库**（推荐 SQLite 初期，后续可换 MySQL）：

  * 库：`storage/baijiahao.db`
  * 表：`articles`、`authors`、`fetch_logs`

---

## 3. 需抓取的字段（数据模型）

### 3.1 文章 `Article`

| 字段             | 类型       | 说明                     |
| -------------- | -------- | ---------------------- |
| `article_id`   | TEXT(PK) | 从文章 URL 或页面脚本里解析，作为唯一键 |
| `url`          | TEXT     | 原文 URL                 |
| `title`        | TEXT     | 标题                     |
| `author_id`    | TEXT     | 作者 ID                  |
| `author_name`  | TEXT     | 作者名（可从页面拿）             |
| `publish_time` | DATETIME | 发布时间（解析/标准化为本地时区或 UTC） |
| `content_html` | TEXT     | 原始 HTML（可选）            |
| `content_text` | TEXT     | 纯文本（去标签）               |
| `images`       | JSON     | 图片 URL 列表（或本地存储路径）     |
| `tags`         | JSON     | 文章标签/分类（如有）            |
| `source_raw`   | JSON     | 原始接口/脚本数据（调试可选）        |
| `created_at`   | DATETIME | 抓取时间                   |
| `updated_at`   | DATETIME | 更新/重抓时间                |
| `hash`         | TEXT     | 内容哈希（用于变更检测，选填）        |

### 3.2 作者 `Author`

| 字段             | 类型       | 说明    |
| -------------- | -------- | ----- |
| `author_id`    | TEXT(PK) | 唯一 ID |
| `name`         | TEXT     | 作者名称  |
| `homepage_url` | TEXT     | 主页    |
| `extra`        | JSON     | 其他元数据 |

### 3.3 抓取日志 `FetchLog`

| 字段              | 类型         | 说明                       |
| --------------- | ---------- | ------------------------ |
| `id`            | INTEGER PK | 自增                       |
| `author_id`     | TEXT       | 关联作者                     |
| `status`        | TEXT       | success / partial / fail |
| `article_count` | INT        | 本轮拉取数量                   |
| `message`       | TEXT       | 错误/备注                    |
| `started_at`    | DATETIME   | 开始时间                     |
| `finished_at`   | DATETIME   | 结束时间                     |

---

## 4. 目标页面与定位思路（示例）

> 典型作者主页示例（占位）：
> `https://author.baidu.com/home/1640549925951234`

解析路径（以**示意**为主，实际以页面为准）：

* 作者主页里会有“最新”、“文章列表”模块；列表项中包含文章跳转链接，形如：
  `https://baijiahao.baidu.com/s?id=XXXXXXX`
* 进入文章页：解析

  * 标题节点（如 `<h1>`/特定 class）
  * 发布时间（页面可见或内嵌 JSON）
  * 正文容器（常为 `<div class="content">...</div>` 类似）
  * 图片 `<img src>`
* 优先使用**稳定的结构/语义化 class**；必要时从**内嵌脚本 JSON**获取数据。
* 遇到懒加载图片，读取 `data-src`/`data-original`。

---

## 5. 技术选型

* **语言**：Python 3.10+
* **依赖**：`requests`（或 `httpx`）、`beautifulsoup4`、`lxml`、`tenacity`（重试）、`loguru`（日志）、`sqlite3`（内置）
* **可选**：`playwright`/`selenium`（若必须渲染 JS 时启用，默认关闭）
* **任务调度**：`cron` / `APScheduler`（二选一）
* **配置**：`config.yaml`（代理、并发、限速、UA 列表、存储开关等）

---

## 6. 目录结构（建议）

```
baijiahao_spider/
├─ app/
│  ├─ main.py                # 入口：命令行解析/调度
│  ├─ crawler.py             # 抓取与解析核心（requests 版）
│  ├─ parser.py              # 页面字段提取
│  ├─ storage.py             # SQLite/文件落地层
│  ├─ downloader.py          # 图片下载（可选）
│  ├─ scheduler.py           # 定时任务（APScheduler/cron wrapper）
│  ├─ utils.py               # UA、随机等待、去重、hash
│  └─ anti_block.py          # 限速、代理、重试策略
├─ data/
│  └─ authors.txt
├─ output/                   # 结果目录
├─ storage/                  # SQLite 数据库存放
├─ config.yaml
├─ requirements.txt
├─ README.md
└─ tests/
   ├─ test_parser.py
   └─ test_storage.py
```

---

## 7. 配置项（`config.yaml` 示例）

```yaml
request:
  timeout: 15
  retry: 3
  backoff: 1.5         # 指数退避基数
  random_ua: true
  headers:
    Accept-Language: zh-CN,zh;q=0.9
  proxies:             # 留空则不启用
    http: ""
    https: ""

throttle:
  min_delay: 1.0       # 每请求之间随机延迟区间
  max_delay: 3.0
  per_author_limit: 5  # 每轮每个作者最多抓取 N 篇最新文章

storage:
  save_json: true
  save_text: true
  save_images: false
  sqlite: true

scheduler:
  enabled: false
  cron: "*/30 * * * *" # 每 30 分钟

debug:
  save_raw_html: false
```

---

## 8. 命令行用法（CLI）

```bash
# 安装依赖
pip install -r requirements.txt

# 单次抓取（读取 data/authors.txt）
python -m app.main run --limit-per-author 5

# 指定作者文件
python -m app.main run --authors-file data/authors.txt

# 仅抓取其中一个作者
python -m app.main run --one https://author.baidu.com/home/1640...

# 启动定时任务（APScheduler）
python -m app.main schedule --cron "*/30 * * * *"
```

参数说明：

* `--limit-per-author`：每位作者本轮最多抓取几篇（默认取配置）。
* `--one`：只抓某一个作者。
* `--debug`：开启调试（保存原始 HTML）。

---

## 9. 去重与断点续抓

* **主键**：`article_id` 唯一；插入前查询/UPSERT。
* **URL 指纹**：对 `url` 取 `md5` 作为次级指纹。
* **增量策略**：从作者列表页按时间倒序，只要遇到**已存在**的文章即可提前停止（减少无效请求）。

---

## 10. 异常与重试

* 使用 `tenacity` 对网络请求/解析做**有限次重试**（如 3 次，指数退避）。
* 捕获并分类错误：`NetworkError / ParseError / RateLimit`。
* 将错误写入 `fetch_logs` 并输出到 `logs/`（可由 `loguru` 滚动日志处理）。

---

## 11. 反爬基础措施

* UA 轮换、Referer 设置。
* 请求间隔随机延迟；每作者/全局的速率限制。
* 可选代理池（HTTP/HTTPS）。
* 若强依赖 JS 渲染再切换到 `playwright`，但默认禁用以降低复杂度与风控风险。

---

## 12. 测试要求（最小集）

* `tests/test_parser.py`：给定示例 HTML 片段，能正确提取标题/时间/正文。
* `tests/test_storage.py`：写入/读取 SQLite 的基本 CRUD；去重逻辑验证。
* `pytest` 在 CI 中运行，必须通过。

---

## 13. CI（GitHub Actions）

* 触发：`push` / `pull_request`。
* 步骤：`setup-python 3.11` → 安装依赖 → `pytest -q`。
* 可选：上传覆盖率（后续）。

---

## 14. 里程碑（MVP → V1）

* **MVP**：requests 直抓、解析 1 位作者、保存 SQLite/JSON、CLI 单次运行。
* **V0.2**：多作者循环、限速与重试、去重。
* **V0.3**：图片下载、日志落地、错误分类。
* **V1.0**：APScheduler 定时、CI、基本测试覆盖、配置化。

---

## 15. 与 Codex 协同（建议指令模板）

> 可粘到 Codex，让它**按分支 + PR**工作流自动生成代码。

```
请从 main 创建新分支：feat/baijiahao-spider。
按《docs/BAIJIAHAO_SPIDER_REQUIREMENTS.md》实现 MVP：
- 目录结构、config.yaml、requirements.txt
- app/main.py（CLI）、app/crawler.py（请求+限速+重试）、app/parser.py（字段解析）、app/storage.py（SQLite+JSON）
- tests/test_parser.py、tests/test_storage.py
- .github/workflows/ci.yml（pytest）
确保：读取 data/authors.txt，抓取每作者最新 <=5 篇文章，去重入库。
完成后提交并推送，创建到 main 的 PR（标题：feat: baijiahao spider MVP），正文写明运行方法与配置项。
```

---

## 16. 法律与伦理

* 遵守目标网站条款、著作权与隐私政策；如对方要求停止抓取，应立即停止。
* 数据仅用于学习与合规允许的范围，不对外分发原文内容。
* 合理控制频率，避免对目标站点造成压力。
