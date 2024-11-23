import pytest
from src.utils.html_parser import HTMLParser
from src.models.html_document import HTMLDocument
from src.exceptions.editor_exceptions import InvalidNodeError

class TestHTMLParser:
    @pytest.fixture
    def valid_html(self):
        return """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <div id="content">
                    <p id="para1">Hello World</p>
                </div>
            </body>
        </html>
        """

    def test_parse_valid_html(self, valid_html):
        """测试解析有效的HTML"""
        document = HTMLParser.parse_html(valid_html)
        
        assert document.root is not None
        assert document.root.tag == 'html'
        assert document.root.find_by_id('content') is not None
        assert document.root.find_by_id('para1').text == 'Hello World'

    def test_parse_invalid_html(self):
        """测试解析无效的HTML"""
        invalid_html = "<div>No HTML root</div>"
        with pytest.raises(InvalidNodeError):
            HTMLParser.parse_html(invalid_html)

    def test_parse_duplicate_ids(self):
        """测试解析包含重复ID的HTML"""
        duplicate_ids_html = """
        <html>
            <body>
                <div id="test">First</div>
                <div id="test">Second</div>
            </body>
        </html>
        """
        with pytest.raises(InvalidNodeError):
            HTMLParser.parse_html(duplicate_ids_html)

    def test_to_html_string(self, valid_html):
        """测试HTML文档转换为字符串"""
        document = HTMLParser.parse_html(valid_html)
        html_string = HTMLParser.to_html_string(document)
        
        # 验证基本结构
        assert '<html>' in html_string
        assert '<head>' in html_string
        assert '<title>Test Page</title>' in html_string
        assert '<div id="content">' in html_string
        assert '<p id="para1">Hello World</p>' in html_string

    def test_to_tree_string(self, valid_html):
        """测试生成树形结构字符串"""
        document = HTMLParser.parse_html(valid_html)
        tree_string = HTMLParser.to_tree_string(document, show_id=True)
        
        # 验证树形结构
        assert 'html' in tree_string
        assert '├── head' in tree_string
        assert '│   └── title' in tree_string
        assert '└── body' in tree_string 