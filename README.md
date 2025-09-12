# 百家号最新文章抓取器

根据 `docs/BAIJIAHAO_SPIDER_REQUIREMENTS.md` 的前10个小章节实现的示例项目，用于从百家号作者主页抓取最新文章并保存。

## 快速开始

```bash
pip install -r requirements.txt
python -m app.main run --limit-per-author 5
```

默认读取 `data/authors.txt` 中的作者主页列表，并将结果保存到 `output/` 目录和 `storage/baijiahao.db`。

更多用法参见需求文档或执行：

```bash
python -m app.main --help
```
