from pathlib import Path
from typing import Optional
from .command import Command
from ..models.html_document import HTMLDocument
from ..utils.html_parser import HTMLParser
from ..exceptions.editor_exceptions import FileOperationError

class IOCommand(Command):
    """IO操作相关的命令基类"""
    
    def __init__(self, document: HTMLDocument):
        """
        初始化IO命令
        
        Args:
            document: 要操作的HTML文档对象
            
        Note:
            IO命令的撤销行为由具体子类实现
        """
        self.document = document
    
    @property
    def can_undo(self) -> bool:
        """
        检查命令是否可以撤销
        
        Returns:
            bool: 可以撤销返回True，否则返回False
        """
        raise NotImplementedError
    
    def undo(self) -> bool:
        """
        撤销命令
        
        Returns:
            bool: 撤销成功返回True，失败返回False
        """
        raise NotImplementedError

class ReadCommand(IOCommand):
    """从文件读取HTML内容的命令"""
    
    def __init__(self, document: HTMLDocument, filepath: Path):
        """
        初始化读取命令
        
        Args:
            document: 目标HTML文档对象
            filepath: 要读取的文件路径
            
        Note:
            - 读取的内容会完全替换当前文档的内容
            - 如果文件不存在或格式错误，读取将失败
            - 读取操作会重置文档的修改状态
            - 读取操作会清空撤销/重做栈
        """
        super().__init__(document)
        self.filepath = filepath
    
    def execute(self) -> bool:
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_document = HTMLParser.parse_html(content)
            # 更新当前文档的内容
            self.document.root = new_document.root
            return True
            
        except (FileOperationError, IOError) as e:
            print(f"读取文件失败: {str(e)}")
            return False
    
    @property
    def can_undo(self) -> bool:
        """读取命令不支持撤销"""
        return False

class SaveCommand(IOCommand):
    """保存HTML内容到文件的命令"""
    
    def __init__(self, document: HTMLDocument, filepath: Path):
        """
        初始化保存命令
        
        Args:
            document: 要保存的HTML文档对象
            filepath: 保存的目标文件路径
            
        Note:
            - 保存成功后会重置文档的修改状态
            - 如果文件路径无效或无写入权限，保存将失败
            - 保存操作不支持撤销
        """
        super().__init__(document)
        self.filepath = filepath
    
    def execute(self) -> bool:
        try:
            content = HTMLParser.to_html_string(self.document)
            with open(self.filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.document.set_unmodified()
            return True
            
        except IOError as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    @property
    def can_undo(self) -> bool:
        """保存命令不支持撤销"""
        return False

class InitCommand(IOCommand):
    """初始化空HTML文档的命令"""
    
    def __init__(self, document: HTMLDocument):
        """
        初始化空文档命令
        
        Args:
            document: 要初始化的HTML文档对象
            
        Note:
            - 会创建一个包含基本HTML结构的空文档
            - 会清除文档的所有现有内容
            - 初始化操作不支持撤销
        """
        super().__init__(document)
    
    @property
    def can_undo(self) -> bool:
        """初始化命令不支持撤销"""
        return False
    
    def execute(self) -> bool:
        try:
            self.document.create_empty_document()
            return True
            
        except Exception as e:
            print(f"初始化文档失败: {str(e)}")
            return False 