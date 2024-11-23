from typing import List, Optional, Dict
from pathlib import Path
from ..models.html_document import HTMLDocument
from ..utils.html_parser import HTMLParser
from ..commands.command import Command
from ..exceptions.editor_exceptions import EditorException, FileOperationError

class Editor:
    """HTML编辑器核心类，管理单个HTML文档的编辑状态"""
    
    def __init__(self, filepath: Optional[Path] = None):
        """
        初始化编辑器实例
        
        Args:
            filepath: HTML文件路径，如果提供则加载该文件，否则创建空文档
        """
        self.filepath: Optional[Path] = filepath
        self.document: Optional[HTMLDocument] = None
        self.show_id: bool = True  # 控制树形显示时是否显示ID
        self._modified: bool = False
        
        # 撤销/重做相关属性
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []
        
        if filepath and filepath.exists():
            self.load_file(filepath)
        else:
            self.init_empty_document()
        
    def init_empty_document(self) -> None:
        """
        初始化一个空的HTML文档
        
        创建一个包含基本HTML结构的空文档，并重置编辑器状态
        """
        self.document = HTMLDocument()
        self.document.create_empty_document()
        self._clear_command_stacks()
        self._modified = False
        
    def load_file(self, filepath: Path) -> bool:
        """
        从文件加载HTML文档
        
        Args:
            filepath: 要加载的HTML文件路径
            
        Returns:
            bool: 加载成功返回True，失败返回False
            
        Note:
            加载失败时会自动创建空文档
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.document = HTMLParser.parse_html(html_content)
            self.filepath = filepath
            self._clear_command_stacks()
            self._modified = False
            return True
            
        except Exception as e:
            print(f"加载文件失败: {str(e)}")
            self.init_empty_document()
            return False
            
    def save_file(self, filepath: Path) -> bool:
        """
        将当前文档保存到文件
        
        Args:
            filepath: 保存的目标文件路径
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            if self.document is None:
                return False
            
            html_content = HTMLParser.to_html_string(self.document)  # 使用HTMLParser
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.filepath = filepath
            self._modified = False
            return True
            
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
            
    def execute_command(self, command: Command) -> bool:
        """
        执行编辑命令
        
        Args:
            command: 要执行的命令对象
            
        Returns:
            bool: 命令执行成功返回True，失败返回False
            
        Note:
            成功执行的命令会被添加到撤销栈中
        """
        try:
            if command.execute():
                self._undo_stack.append(command)
                self._redo_stack.clear()  # 清空重做栈
                self._modified = True  # 设置修改标志
                return True
            return False
        except Exception as e:
            print(f"执行命令失败: {str(e)}")
            return False
        
    def undo(self) -> bool:
        """
        撤销上一个编辑命令
        
        Returns:
            bool: 撤销成功返回True，没有可撤销的命令或撤销失败返回False
            
        Note:
            被撤销的命令会被移到重做栈中
        """
        if not self._undo_stack:
            return False
            
        command = self._undo_stack.pop()
        if command.undo():
            self._redo_stack.append(command)
            self._modified = len(self._undo_stack) > 0  # 根据撤销栈状态设置修改标志
            return True
        
        self._undo_stack.append(command)  # 撤销失败，恢复命令
        return False
        
    def redo(self) -> bool:
        """
        重做上一个被撤销的命令
        
        Returns:
            bool: 重做成功返回True，没有可重做的命令或重做失败返回False
            
        Note:
            重做的命令会被移回撤销栈中
        """
        if not self._redo_stack:
            return False
            
        command = self._redo_stack.pop()
        if command.execute():
            self._undo_stack.append(command)
            self._modified = True  # 重做成功后设置修改标志
            return True
        
        self._redo_stack.append(command)  # 重做失败，恢复命令
        return False
        
    def _clear_command_stacks(self) -> None:
        """
        清空撤销和重做命令栈
        
        在加载新文件或创建空文档时调用
        """
        self._undo_stack.clear()
        self._redo_stack.clear()
        
    def get_tree_view(self) -> str:
        """
        获取文档的树形结构视图
        
        Returns:
            str: 树形格式的文档结构字符串，如果文档为空返回空字符串
            
        Note:
            树形视图会根据show_id属性决定是否显示节点ID
        """
        if not self.document:
            return ""
        return HTMLParser.to_tree_string(self.document, self.show_id)
        
    def get_indented_view(self, indent: int = 2) -> str:
        """
        获取文档的缩进格式视图
        
        Args:
            indent: 每级缩进的空格数
            
        Returns:
            str: 缩进格式的HTML字符串，如果文档为空返回空字符串
        """
        if not self.document:
            return ""
        return HTMLParser.to_html_string(self.document, indent)
        
    @property
    def is_modified(self) -> bool:
        """
        获取文档的修改状态
        
        Returns:
            bool: 如果文档自上次保存后被修改返回True，否则返回False
        """
        return self._modified
        
    @property
    def filename(self) -> Optional[str]:
        """
        获取当前文件名
        
        Returns:
            Optional[str]: 当前打开文件的文件名，如果没有打开文件则返回None
        """
        return self.filepath.name if self.filepath else None 