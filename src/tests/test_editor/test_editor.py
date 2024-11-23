import pytest
from pathlib import Path
from src.editor.editor import Editor
from src.commands.edit_commands import EditTextCommand
from src.commands.command import Command

class TestEditor:
    @pytest.fixture
    def sample_html_file(self, tmp_path):
        """创建示例HTML文件"""
        html_file = tmp_path / "test.html"
        html_content = """
        <html>
            <head><title>Test</title></head>
            <body><p id="test">Original content</p></body>
        </html>
        """
        html_file.write_text(html_content)
        return html_file

    @pytest.fixture
    def editor(self, sample_html_file):
        """创建编辑器实例"""
        editor = Editor()
        editor.load_file(sample_html_file)
        return editor

    def test_load_document(self, editor):
        """测试加载文档"""
        assert editor.document is not None
        assert editor.document.root.find_by_id('test').text == 'Original content'

    def test_save_document(self, editor, tmp_path):
        """测试保存文档"""
        save_path = tmp_path / "saved.html"
        
        # 修改文档
        command = EditTextCommand(editor.document, 'test', 'Modified content')
        editor.execute_command(command)
        
        # 保存文档
        assert editor.save_file(save_path)
        
        # 验证文件内容
        saved_content = save_path.read_text()
        assert 'Modified content' in saved_content

    def test_command_execution_and_undo(self, editor):
        """测试命令执行和撤销"""
        # 执行编辑命令
        command = EditTextCommand(editor.document, 'test', 'New content')
        assert editor.execute_command(command)
        assert editor.document.root.find_by_id('test').text == 'New content'
        
        # 测试撤销
        assert editor.undo()
        assert editor.document.root.find_by_id('test').text == 'Original content'
        
        # 测试重做
        assert editor.redo()
        assert editor.document.root.find_by_id('test').text == 'New content'

    def test_multiple_commands(self, editor):
        """测试多个命令的执行和撤销"""
        # 添加调试信息
        print("\nInitial text:", editor.document.root.find_by_id('test').text)
        
        # 执行多个命令
        commands = [
            EditTextCommand(editor.document, 'test', 'First edit'),
            EditTextCommand(editor.document, 'test', 'Second edit')
        ]
        
        # 逐个执行命令并验证
        for i, command in enumerate(commands):
            assert editor.execute_command(command)
            current_text = editor.document.root.find_by_id('test').text
            print(f"After command {i+1}, text:", current_text)
        
        # 验证最终状态
        final_text = editor.document.root.find_by_id('test').text
        print("Final text:", final_text)
        assert final_text == 'Second edit'

    def test_modified_flag(self, editor):
        """测试文档修改标志"""
        assert not editor.is_modified
        
        # 执行修改
        command = EditTextCommand(editor.document, 'test', 'Modified')
        editor.execute_command(command)
        assert editor.is_modified
        
        # 保存后清除修改标志
        editor.save_file(editor.filepath)
        assert not editor.is_modified 

    def test_editor_error_handling(self, editor):
        """测试编辑器错误处理"""
        # 测试加载不存在的文件
        assert not editor.load_file(Path("nonexistent.html"))
        
        # 测试保存到无效路径
        assert not editor.save_file(Path("/invalid/path/file.html"))
        
        # 测试执行无效命令
        invalid_command = Command()  # 基础命令
        assert not editor.execute_command(invalid_command)

    def test_editor_state_management(self, editor):
        """测试编辑器状态管理"""
        # 测试撤销栈为空时的撤销
        assert not editor.undo()
        
        # 测试重做栈为空时的重做
        assert not editor.redo()
        
        # 测试清空命令历史
        command = EditTextCommand(editor.document, 'test', 'New content')
        editor.execute_command(command)
        editor._clear_command_stacks()
        assert not editor.undo()  # 清空后应该无法撤销

    def test_editor_multiple_operations(self, editor):
        """测试编辑器多重操作"""
        # 执行多个命令并验证状态
        commands = [
            EditTextCommand(editor.document, 'test', f'Content {i}')
            for i in range(5)
        ]
        
        # 执行所有命令
        for cmd in commands:
            assert editor.execute_command(cmd)
        
        # 测试多次撤销和重做
        for _ in range(3):
            assert editor.undo()
        
        for _ in range(2):
            assert editor.redo()