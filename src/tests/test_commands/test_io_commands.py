import pytest
from pathlib import Path
from src.commands.io_commands import SaveCommand, InitCommand, ReadCommand
from src.models.html_document import HTMLDocument
from src.exceptions.editor_exceptions import FileOperationError

class TestIOCommands:
    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = HTMLDocument()
        doc.create_empty_document()
        return doc

    @pytest.fixture
    def temp_html_file(self, tmp_path):
        """创建临时HTML文件"""
        return tmp_path / "test.html"

    def test_save_command(self, sample_document, temp_html_file):
        """测试保存命令"""
        # 修改文档内容
        body = sample_document.root.find_by_id('body')
        body.text = "Test content"
        
        # 执行保存命令
        command = SaveCommand(sample_document, temp_html_file)
        assert command.execute()
        
        # 验证文件内容
        assert temp_html_file.exists()
        content = temp_html_file.read_text()
        assert 'Test content' in content
        assert not sample_document.is_modified

    def test_save_command_invalid_path(self, sample_document, tmp_path):
        """测试保存到无效路径"""
        invalid_path = tmp_path / "nonexistent" / "test.html"
        command = SaveCommand(sample_document, invalid_path)
        
        # 保存应该失败
        assert not command.execute()

    def test_init_command(self):
        """测试初始化命令"""
        doc = HTMLDocument()
        command = InitCommand(doc)
        
        # 执行初始化
        assert command.execute()
        
        # 验证文档结构
        assert doc.root is not None
        assert doc.root.tag == 'html'
        assert len(doc.root.children) == 2
        assert doc.root.find_by_id('head') is not None
        assert doc.root.find_by_id('body') is not None
        assert not doc.is_modified

    def test_read_command(self, temp_html_file):
        """测试读取命令"""
        # 创建测试文件
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body><p id="test">Test content</p></body>
        </html>
        """
        temp_html_file.write_text(html_content)
        
        # 执行读取命令
        doc = HTMLDocument()
        command = ReadCommand(doc, temp_html_file)
        assert command.execute()
        
        # 验证文档内容
        assert doc.root is not None
        assert doc.root.find_by_id('test') is not None
        assert doc.root.find_by_id('test').text == 'Test content'
        assert not doc.is_modified

    def test_read_command_nonexistent_file(self):
        """测试读取不存在的文件"""
        doc = HTMLDocument()
        command = ReadCommand(doc, Path("nonexistent.html"))
        assert not command.execute()

    def test_io_commands_undo(self, sample_document, temp_html_file):
        """测试IO命令的撤销行为"""
        # IO命令不应支持撤销
        save_command = SaveCommand(sample_document, temp_html_file)
        init_command = InitCommand(sample_document)
        read_command = ReadCommand(sample_document, temp_html_file)
        
        assert not save_command.can_undo
        assert not init_command.can_undo
        assert not read_command.can_undo 