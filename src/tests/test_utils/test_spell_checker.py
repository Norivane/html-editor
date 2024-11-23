import pytest
from src.utils.spell_checker import SpellChecker
from src.models.html_document import HTMLDocument
from src.utils.html_parser import HTMLParser

class TestSpellChecker:
    @pytest.fixture
    def spell_checker(self):
        return SpellChecker()

    @pytest.fixture
    def sample_document(self):
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <div id="content">
                    <p id="para1">This is a misspeled word.</p>
                    <p id="para2">Another incorrekt sentence.</p>
                </div>
            </body>
        </html>
        """
        return HTMLParser.parse_html(html_content)

    def test_check_document(self, spell_checker, sample_document):
        """测试文档拼写检查"""
        errors = spell_checker.check_document(sample_document)
        
        # 验证发现的错误
        assert 'para1' in errors
        assert 'para2' in errors
        
        # 验证错误详情
        para1_errors = errors['para1']
        assert any('misspeled' in str(error) for error in para1_errors)
        
        para2_errors = errors['para2']
        assert any('incorrekt' in str(error) for error in para2_errors)

    def test_ignored_words(self, spell_checker):
        """测试忽略的单词"""
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <div id="test">
                    This is a div with css and html.
                </div>
            </body>
        </html>
        """
        document = HTMLParser.parse_html(html_content)
        errors = spell_checker.check_document(document)
        
        # 验证忽略的技术术语没有被标记为错误
        assert 'test' not in errors or not any('div' in str(error) for error in errors.get('test', []))
        assert 'test' not in errors or not any('css' in str(error) for error in errors.get('test', []))
        assert 'test' not in errors or not any('html' in str(error) for error in errors.get('test', []))

    def test_empty_document(self, spell_checker):
        """测试空文档"""
        document = HTMLDocument()
        document.create_empty_document()
        errors = spell_checker.check_document(document)
        assert not errors 

    def test_compound_words(self, spell_checker):
        """测试复合词检查"""
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body>
                <p id="test">web-based application</p>
            </body>
        </html>
        """
        document = HTMLParser.parse_html(html_content)
        errors = spell_checker.check_document(document)
        assert 'test' not in errors  # web-based 应该被识别为有效

    def test_camelcase_words(self, spell_checker):
        """测试驼峰命名词检查"""
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body>
                <p id="test">JavaScript TypeScript</p>
            </body>
        </html>
        """
        document = HTMLParser.parse_html(html_content)
        errors = spell_checker.check_document(document)
        assert 'test' not in errors  # 驼峰命名应该被正确处理