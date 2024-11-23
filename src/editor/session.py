from typing import Dict, Optional, List
from pathlib import Path
import json
from .editor import Editor
from ..exceptions.editor_exceptions import EditorException
from ..utils.html_parser import HTMLParser

class Session:
    """编辑器会话管理类，管理多个编辑器实例和会话状态"""
    
    SESSION_FILE = Path("session.json")  # 会话信息保存文件
    
    def __init__(self):
        """
        初始化会话管理器
        
        Note:
            会自动尝试从session.json恢复上次会话状态
        """
        self.editors: Dict[str, Editor] = {}  # 文件名 -> 编辑器实例的映射
        self.active_editor: Optional[Editor] = None  # 当前活动的编辑器
        self.restore_session()  # 恢复上次会话状态
    
    def load_file(self, filepath: Path) -> bool:
        """
        加载文件到编辑器
        
        Args:
            filepath: 要加载的文件路径
            
        Returns:
            bool: 加载成功返回True，失败返回False
            
        Note:
            如果文件已经打开，会切换到对应的编辑器而不是重新加载
        """
        try:
            filename = str(filepath)
            if filename in self.editors:
                self.active_editor = self.editors[filename]
                return True
            
            editor = Editor(filepath)
            editor.load_file(filepath)
            self.editors[filename] = editor
            self.active_editor = editor
            return True
            
        except EditorException as e:
            print(f"加载文件失败: {str(e)}")
            return False
    
    def create_new_file(self, filepath: Path) -> bool:
        """
        创建新的HTML文件
        
        Args:
            filepath: 新文件的路径
            
        Returns:
            bool: 创建成功返回True，失败返回False
            
        Note:
            - 如果文件路径已存在对应的编辑器，则创建失败
            - 会立即将空文档保存到文件系统
        """
        try:
            filename = str(filepath)
            if filename in self.editors:
                print(f"文件 {filename} 已经打开")
                return False
            
            # 创建新的编辑器实例
            editor = Editor(filepath)
            editor.init_empty_document()
            
            # 保存空文档到文件系统
            content = HTMLParser.to_html_string(editor.document)
            filepath.write_text(content, encoding='utf-8')
            
            # 将编辑器添加到会话中
            self.editors[filename] = editor
            self.active_editor = editor
            return True
            
        except Exception as e:
            print(f"创建文件失败: {str(e)}")
            return False
    
    def close_editor(self, filepath: Path) -> bool:
        """
        关闭指定文件的编辑器
        
        Args:
            filepath: 要关闭的文件路径
            
        Returns:
            bool: 关闭成功返回True，失败返回False
            
        Note:
            - 如果文件已修改，会提示保存
            - 关闭当前活动编辑器时会自动切换到其他编辑器
        """
        filename = str(filepath)
        editor = self.editors.get(filename)
        if not editor:
            return False
        
        if editor.is_modified:
            response = input(f"文件 {filename} 已修改，是否保存? (y/n): ")
            if response.lower() == 'y':
                editor.save_file()
        
        del self.editors[filename]
        if self.active_editor == editor:
            self.active_editor = next(iter(self.editors.values())) if self.editors else None
        return True
    
    def switch_editor(self, filepath: Path) -> bool:
        """
        切换当前活动的编辑器
        
        Args:
            filepath: 要切换到的文件路径
            
        Returns:
            bool: 切换成功返回True，文件未打开返回False
        """
        filename = str(filepath)
        if filename not in self.editors:
            return False
        
        self.active_editor = self.editors[filename]
        return True
    
    def save_session(self) -> None:
        """
        保存当前会话状态到文件
        
        Note:
            - 保存所有打开的文件路径
            - 保存当前活动文件
            - 保存每个编辑器的显示设置
            - 保存到 session.json 文件
        """
        session_data = {
            "files": [],
            "active_file": None
        }
        
        for filename, editor in self.editors.items():
            file_data = {
                "path": filename,
                "show_id": editor.show_id
            }
            session_data["files"].append(file_data)
            
            if editor == self.active_editor:
                session_data["active_file"] = filename
        
        try:
            with open(self.SESSION_FILE, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
        except IOError as e:
            print(f"保存会话状态失败: {str(e)}")
    
    def restore_session(self) -> None:
        """
        从文件恢复上次会话状态
        
        Note:
            - 尝试加载上次打开的所有文件
            - 恢复编辑器显示设置
            - 恢复上次的活动文件
            - 如果session.json不存在或损坏，会静默失败
        """
        if not self.SESSION_FILE.exists():
            return
        
        try:
            with open(self.SESSION_FILE, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            for file_data in session_data["files"]:
                filepath = Path(file_data["path"])
                if filepath.exists():
                    self.load_file(filepath)
                    editor = self.editors[str(filepath)]
                    editor.show_id = file_data["show_id"]
            
            active_file = session_data.get("active_file")
            if active_file and active_file in self.editors:
                self.active_editor = self.editors[active_file]
                
        except (IOError, json.JSONDecodeError) as e:
            print(f"恢复会话状态失败: {str(e)}") 