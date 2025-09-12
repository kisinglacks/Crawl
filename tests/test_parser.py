from app import parser

SAMPLE_HTML = """
<html>
<head><title>t</title></head>
<body>
<h1>示例标题</h1>
<time datetime="2024-01-01T00:00:00"></time>
<div class="content">
<p>内容段落</p>
<img src="https://example.com/a.jpg" />
</div>
</body>
</html>
"""


def test_parse_article():
    art = parser.parse_article(SAMPLE_HTML, "https://baijiahao.baidu.com/s?id=123", "111", "作者")
    assert art.article_id == "123"
    assert art.title == "示例标题"
    assert "内容段落" in art.content_text
    assert art.images == ["https://example.com/a.jpg"]
