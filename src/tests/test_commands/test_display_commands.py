import pytest
from io import StringIO
from contextlib import redirect_stdout
from src.commands.display_commands import PrintTreeCommand, PrintIndentCommand, SpellCheckCommand
from src.utils.html_parser import HTMLParser

class TestDisplayCommands:
    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
            </head>
            <body>
                <div id="content">
                    <p id="para1">This is a test paragraph.</p>
                    <ul id="list">
                        <li id="item1">First item</li>
                        <li id="item2">Second item</li>
                    </ul>
                </div>
            </body>
        </html>
        """
        return HTMLParser.parse_html(html_content)

    def test_print_tree_command(self, sample_document):
        """测试树形显示命令"""
        command = PrintTreeCommand(sample_document, show_id=True)
        
        # 捕获标准输出
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证输出格式
        assert 'html' in result
        assert '├── head' in result
        assert '│   └── title' in result
        assert '└── body' in result
        assert '    └── div#content' in result
        assert '        ├── p#para1' in result
        assert '        └── ul#list' in result
        assert '            ├── li#item1' in result
        assert '            └── li#item2' in result

    def test_print_tree_without_ids(self, sample_document):
        """测试不显示ID的树形显示"""
        command = PrintTreeCommand(sample_document, show_id=False)
        
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证输出不包含ID
        assert '[content]' not in result
        assert '[para1]' not in result
        assert 'div' in result
        assert 'p' in result

    def test_print_indent_command(self, sample_document):
        """测试缩进显示命令"""
        command = PrintIndentCommand(sample_document, indent=2)
        
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证缩进格式
        assert '<html>' in result
        assert '  <head>' in result
        assert '    <title>Test Page</title>' in result
        assert '  <body>' in result
        assert '    <div id="content">' in result
        assert '      <p id="para1">This is a test paragraph.</p>' in result

    def test_print_indent_custom_indent(self, sample_document):
        """测试自定义缩进值"""
        command = PrintIndentCommand(sample_document, indent=4)
        
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证4空格缩进
        assert '<html>' in result
        assert '    <head>' in result
        assert '        <title>Test Page</title>' in result

    def test_spell_check_command(self, sample_document):
        """测试拼写检查命令"""
        # 修改文档中的文本包含拼写错误
        para = sample_document.root.find_by_id('para1')
        para.text = "This is a misspeled word"
        
        command = SpellCheckCommand(sample_document)
        
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证拼写检查结果
        assert '拼写错误' in result
        assert 'misspeled' in result

    def test_spell_check_no_errors(self, sample_document):
        """测试无拼写错误的情况"""
        # 确保文本全部拼写正确
        para = sample_document.root.find_by_id('para1')
        para.text = "This is a correctly spelled sentence."
        
        command = SpellCheckCommand(sample_document)
        
        output = StringIO()
        with redirect_stdout(output):
            command.execute()
        
        result = output.getvalue()
        
        # 验证输出显示无错误
        assert '未发现拼写错误' in result

    def test_display_commands_undo(self, sample_document):
        """测试显示命令的撤销行为"""
        # 显示命令不应支持撤销
        tree_command = PrintTreeCommand(sample_document, show_id=True)
        indent_command = PrintIndentCommand(sample_document)
        spell_command = SpellCheckCommand(sample_document)
        
        assert not tree_command.can_undo
        assert not indent_command.can_undo
        assert not spell_command.can_undo 