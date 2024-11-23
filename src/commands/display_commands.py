from typing import Optional
from .command import Command
from ..models.html_document import HTMLDocument
from ..utils.html_parser import HTMLParser
from ..utils.spell_checker import SpellChecker

class DisplayCommand(Command):
    """显示相关的命令基类，提供显示HTML文档内容的基本功能"""
    
    def __init__(self, document: HTMLDocument):
        """
        初始化显示命令
        
        Args:
            document: 要显示的HTML文档对象
            
        Note:
            所有显示命令都不支持撤销操作
        """
        self.document = document
    
    @property
    def can_undo(self) -> bool:
        """显示命令不支持撤销"""
        return False
    
    def undo(self) -> bool:
        """显示命令不支持撤销"""
        return False

class PrintTreeCommand(DisplayCommand):
    """以树形结构显示HTML文档的命令，可选择是否显示节点ID和拼写错误标记"""
    
    def __init__(self, document: HTMLDocument, show_id: bool = True):
        """
        初始化树形显示命令
        
        Args:
            document: 要显示的HTML文档对象
            show_id: 是否在显示时包含节点ID，默认为True
            
        Note:
            会自动进行拼写检查并在树形显示中标记错误
        """
        super().__init__(document)
        self.show_id = show_id
        self.spell_checker = SpellChecker()
    
    def execute(self) -> bool:
        if not self.document:
            return False
            
        # 获取拼写检查结果
        spell_errors = self.spell_checker.check_document(self.document)
        
        # 显示树形结构，包含拼写错误标记
        print(HTMLParser.to_tree_string(self.document, self.show_id, spell_errors))
        return True

class PrintIndentCommand(DisplayCommand):
    """以缩进格式显示HTML文档的命令，用于展示文档的源代码形式"""
    
    def __init__(self, document: HTMLDocument, indent: int = 2):
        """
        初始化缩进显示命令
        
        Args:
            document: 要显示的HTML文档对象
            indent: 每级缩进的空格数，默认为2
            
        Note:
            输出格式为标准的HTML源代码格式
        """
        super().__init__(document)
        self.indent = indent
    
    def execute(self) -> bool:
        if not self.document:
            return False
        
        indented_view = HTMLParser.to_html_string(self.document, self.indent)
        print(indented_view)
        return True

class SpellCheckCommand(DisplayCommand):
    """执行拼写检查并显示详细结果的命令"""
    
    def __init__(self, document: HTMLDocument):
        """
        初始化拼写检查命令
        
        Args:
            document: 要检查的HTML文档对象
            
        Note:
            - 会检查文档中所有文本节点的拼写
            - 对于每个错误会显示原文本、错误单词和建议的修正
            - 自动忽略HTML相关的技术术语
            - 支持检查复合词和驼峰命名
            - 显示命令不会修改文档内容
        """
        super().__init__(document)
        self.spell_checker = SpellChecker()
    
    def execute(self) -> bool:
        if not self.document:
            return False
        
        errors = self.spell_checker.check_document(self.document)
        if not errors:
            print("未发现拼写错误。")
            return True
        
        print("发现以下拼写错误：")
        for node_id, node_errors in errors.items():
            if not node_errors:
                continue
            
            print(f"\n节点 {node_id}:")
            for error in node_errors:
                print(f"  句子：{error['text']}")
                print("  拼写可能有误的单词：")
                for word in error['misspelled']:
                    if word in error['suggestions']:
                        suggestions = error['suggestions'][word]
                        if isinstance(suggestions, (list, tuple, set)):
                            suggestions_str = ', '.join(suggestions)
                            print(f"    - {word}: {suggestions_str}")
                        else:
                            print(f"    - {word}: {suggestions}")
        
        return True 