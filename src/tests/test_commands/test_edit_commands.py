import pytest
from src.commands.edit_commands import (
    InsertCommand, AppendCommand, DeleteCommand,
    EditIdCommand, EditTextCommand
)
from src.models.html_document import HTMLDocument
from src.utils.html_parser import HTMLParser

class TestEditCommands:
    @pytest.fixture
    def sample_document(self):
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <div id="content">
                    <p id="para1">Original text</p>
                </div>
            </body>
        </html>
        """
        return HTMLParser.parse_html(html_content)

    def test_insert_command(self, sample_document):
        """测试插入命令"""
        command = InsertCommand(
            sample_document,
            'p',
            'new-para',
            'para1',
            'New paragraph'
        )
        
        # 执行插入
        assert command.execute()
        
        # 验证插入结果
        new_node = sample_document.root.find_by_id('new-para')
        assert new_node is not None
        assert new_node.text == 'New paragraph'
        
        # 测试撤销
        assert command.undo()
        assert sample_document.root.find_by_id('new-para') is None

    def test_append_command(self, sample_document):
        """测试追加命令"""
        command = AppendCommand(
            sample_document,
            'span',
            'new-span',
            'content',
            'Appended text'
        )
        
        # 执行追加
        assert command.execute()
        
        # 验证追加结果
        new_node = sample_document.root.find_by_id('new-span')
        assert new_node is not None
        assert new_node.text == 'Appended text'
        assert new_node.parent.id == 'content'
        
        # 测试撤销
        assert command.undo()
        assert sample_document.root.find_by_id('new-span') is None

    def test_delete_command(self, sample_document):
        """测试删除命令"""
        command = DeleteCommand(sample_document, 'para1')
        
        # 保存原始状态
        original_parent = sample_document.root.find_by_id('para1').parent
        
        # 执行删除
        assert command.execute()
        assert sample_document.root.find_by_id('para1') is None
        
        # 测试撤销
        assert command.undo()
        restored_node = sample_document.root.find_by_id('para1')
        assert restored_node is not None
        assert restored_node.parent == original_parent

    def test_edit_id_command(self, sample_document):
        """测试编辑ID命令"""
        command = EditIdCommand(sample_document, 'para1', 'new-id')
        
        # 执行ID修改
        assert command.execute()
        assert sample_document.root.find_by_id('new-id') is not None
        assert sample_document.root.find_by_id('para1') is None
        
        # 测试撤销
        assert command.undo()
        assert sample_document.root.find_by_id('para1') is not None
        assert sample_document.root.find_by_id('new-id') is None

    def test_edit_text_command(self, sample_document):
        """测试编辑文本命令"""
        command = EditTextCommand(sample_document, 'para1', 'Updated text')
        
        # 保存原始文本
        original_text = sample_document.root.find_by_id('para1').text
        
        # 执行文本修改
        assert command.execute()
        assert sample_document.root.find_by_id('para1').text == 'Updated text'
        
        # 测试撤销
        assert command.undo()
        assert sample_document.root.find_by_id('para1').text == original_text 

    def test_insert_command_invalid_location(self, sample_document):
        """测试在无效位置插入节点"""
        command = InsertCommand(
            sample_document,
            'p',
            'new-para',
            'nonexistent-id',  # 不存在的位置
            'New paragraph'
        )
        assert not command.execute()

    def test_edit_text_nonexistent_node(self, sample_document):
        """测试编辑不存在节点的文本"""
        command = EditTextCommand(sample_document, 'nonexistent', 'New text')
        assert not command.execute()

    def test_duplicate_id_insert(self, sample_document):
        """测试插入重复ID的节点"""
        command = InsertCommand(
            sample_document,
            'p',
            'para1',  # 已存在的ID
            'content',
            'New text'
        )
        assert not command.execute()

    def test_edit_commands_with_empty_document(self, sample_document):
        """测试空文档的编辑命令"""
        # 清空文档
        sample_document.root = None
        
        # 测试各种编辑命令
        insert_cmd = InsertCommand(sample_document, 'p', 'new-id', 'parent-id', 'text')
        assert not insert_cmd.execute()
        
        append_cmd = AppendCommand(sample_document, 'p', 'new-id', 'parent-id', 'text')
        assert not append_cmd.execute()
        
        delete_cmd = DeleteCommand(sample_document, 'some-id')
        assert not delete_cmd.execute()

    def test_edit_commands_with_invalid_parameters(self, sample_document):
        """测试无效参数的编辑命令"""
        # 测试空ID
        insert_cmd = InsertCommand(sample_document, 'p', '', 'para1', 'text')
        assert not insert_cmd.execute()
        
        # 测试无效标签
        append_cmd = AppendCommand(sample_document, '', 'new-id', 'para1', 'text')
        assert not append_cmd.execute()
        
        # 测试编辑ID命令的特殊情况
        edit_id_cmd = EditIdCommand(sample_document, 'para1', 'head')  # head是保留ID
        assert not edit_id_cmd.execute()