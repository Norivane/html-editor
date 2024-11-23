import pytest
import json
from pathlib import Path
from src.editor.session import Session
from src.editor.editor import Editor

class TestSession:
    @pytest.fixture
    def temp_session_file(self, tmp_path):
        """创建临时会话文件"""
        session_file = tmp_path / "session.json"
        return session_file

    @pytest.fixture
    def sample_html_file(self, tmp_path):
        """创建示例HTML文件"""
        html_file = tmp_path / "test.html"
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body><p id="test">Test content</p></body>
        </html>
        """
        html_file.write_text(html_content)
        return html_file

    def test_create_new_file(self, temp_session_file, tmp_path):
        """测试创建新文件"""
        session = Session()
        new_file = tmp_path / "new.html"
        
        # 创建新文件
        assert session.create_new_file(new_file)
        assert new_file.exists()
        assert session.active_editor is not None
        assert session.active_editor.filepath == new_file
        
        # 验证文档结构
        doc = session.active_editor.document
        assert doc.root is not None
        assert doc.root.tag == 'html'
        assert doc.root.find_by_id('head') is not None
        assert doc.root.find_by_id('body') is not None

    def test_load_file(self, sample_html_file):
        """测试加载文件"""
        session = Session()
        
        # 加载文件
        assert session.load_file(sample_html_file)
        assert session.active_editor is not None
        assert session.active_editor.filepath == sample_html_file
        
        # 验证文档内容
        doc = session.active_editor.document
        assert doc.root.find_by_id('test').text == 'Test content'

    def test_switch_editor(self, sample_html_file, tmp_path):
        """测试切换编辑器"""
        session = Session()
        file1 = sample_html_file
        file2 = tmp_path / "another.html"
        
        # 加载两个文件
        session.load_file(file1)
        session.create_new_file(file2)
        
        # 切换编辑器
        assert session.switch_editor(file1)
        assert session.active_editor.filepath == file1
        
        assert session.switch_editor(file2)
        assert session.active_editor.filepath == file2
        
        # 测试切换到不存在的文件
        assert not session.switch_editor(tmp_path / "nonexistent.html")

    def test_close_editor(self, sample_html_file):
        """测试关闭编辑器"""
        session = Session()
        session.load_file(sample_html_file)
        
        # 关闭编辑器
        assert session.close_editor(sample_html_file)
        assert sample_html_file not in session.editors
        assert session.active_editor is None

    def test_save_and_restore_session(self, temp_session_file, sample_html_file):
        """测试保存和恢复会话状态"""
        # 创建并配置会话
        session = Session()
        session.SESSION_FILE = temp_session_file
        session.load_file(sample_html_file)
        session.active_editor.show_id = True
        
        # 保存会话
        session.save_session()
        assert temp_session_file.exists()
        
        # 创建新会话并恢复
        new_session = Session()
        new_session.SESSION_FILE = temp_session_file
        new_session.restore_session()
        
        # 验证恢复的状态
        assert str(sample_html_file) in new_session.editors
        assert new_session.active_editor is not None
        assert new_session.active_editor.show_id is True 