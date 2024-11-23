from typing import Optional, Dict, Any
from .command import Command
from ..models.html_document import HTMLDocument
from ..models.html_node import HTMLNode
from ..exceptions.editor_exceptions import InvalidNodeError, DuplicateIdError

class EditCommand(Command):
    """编辑操作相关的命令基类"""
    
    def __init__(self, document: HTMLDocument):
        """
        初始化编辑命令
        
        Args:
            document: 要编辑的HTML文档对象
        """
        self.document = document

class InsertCommand(EditCommand):
    """在指定位置插入新节点的命令"""
    
    def __init__(self, document: HTMLDocument, tag_name: str, id_value: str, 
                 insert_location: str, text_content: str = ""):
        """
        初始化插入命令
        
        Args:
            document: 目标HTML文档对象
            tag_name: 新节点的标签名称
            id_value: 新节点的唯一标识符
            insert_location: 目标插入位置的节点ID
            text_content: 新节点的文本内容，默认为空字符串
            
        Note:
            - 新节点将被插入到insert_location指定的节点之前
            - id_value在整个文档中必须唯一
            - 如果目标位置无效或ID重复，插入将失败
            - 插入操作可以撤销，会保存插入的节点用于撤销
            - 插入失败时不会修改文档状态
        """
        super().__init__(document)
        self.tag_name = tag_name
        self.id_value = id_value
        self.insert_location = insert_location
        self.text_content = text_content
        self.inserted_node: Optional[HTMLNode] = None
        
    def execute(self) -> bool:
        try:
            # 先检查目标节点是否存在
            target_node = self.document.get_node_by_id(self.insert_location)
            if not target_node:
                print(f"错误：未找到目标节点 '{self.insert_location}'")
                return False
                
            # 检查父节点是否存在
            if not target_node.parent:
                print(f"错误：目标节点 '{self.insert_location}' 没有父节点")
                return False
                
            new_node = HTMLNode(self.tag_name, self.id_value, self.text_content)
            self.document.insert_node(new_node, self.insert_location)
            self.inserted_node = new_node
            return True
        except InvalidNodeError as e:
            print(f"错误：{str(e)}")
            return False
        except DuplicateIdError as e:
            print(f"错误：{str(e)}")
            return False
            
    def undo(self) -> bool:
        if self.inserted_node:
            try:
                self.document.delete_node(self.inserted_node.id)
                return True
            except InvalidNodeError:
                return False
        return False
        
    @property
    def can_undo(self) -> bool:
        return self.inserted_node is not None

class AppendCommand(EditCommand):
    """将新节点添加为指定父节点的子节点的命令"""
    
    def __init__(self, document: HTMLDocument, tag_name: str, id_value: str, 
                 parent_id: str, text_content: str = ""):
        """
        初始化追加命令
        
        Args:
            document: 目标HTML文档对象
            tag_name: 新节点的标签名称
            id_value: 新节点的唯一标识符
            parent_id: 父节点的ID
            text_content: 新节点的文本内容，默认为空字符串
            
        Note:
            - 新节点将被添加到父节点的子节点列表末尾
            - id_value在整个文档中必���唯一
            - 如果父节点不存在或ID重复，追加将失败
        """
        super().__init__(document)
        self.tag_name = tag_name
        self.id_value = id_value
        self.parent_id = parent_id
        self.text_content = text_content
        self.appended_node: Optional[HTMLNode] = None
        
    def execute(self) -> bool:
        try:
            # 检查标签名是否为空
            if not self.tag_name:
                print("错误：标签名不能为空")
                return False
            
            # 先检查父节点是否存在
            parent_node = self.document.get_node_by_id(self.parent_id)
            if not parent_node:
                print(f"错误：未找到父节点 '{self.parent_id}'")
                return False
                
            new_node = HTMLNode(self.tag_name, self.id_value, self.text_content)
            self.document.append_node(new_node, self.parent_id)
            self.appended_node = new_node
            return True
        except InvalidNodeError as e:
            print(f"错误：{str(e)}")
            return False
        except DuplicateIdError as e:
            print(f"错误：{str(e)}")
            return False
            
    def undo(self) -> bool:
        if self.appended_node:
            try:
                self.document.delete_node(self.appended_node.id)
                return True
            except InvalidNodeError:
                return False
        return False
        
    @property
    def can_undo(self) -> bool:
        return self.appended_node is not None

class DeleteCommand(EditCommand):
    """删除指定节点的命令"""
    
    def __init__(self, document: HTMLDocument, node_id: str):
        """
        初始化删除命令
        
        Args:
            document: 目标HTML文档对象
            node_id: 要删除的节点ID
            
        Note:
            - 删除节点时会同时删除其所有子节点
            - 删除操作可以撤销，会保存节点的完整状态
            - 如果节点不存在，删除将失败
        """
        super().__init__(document)
        self.node_id = node_id
        self.deleted_node: Optional[HTMLNode] = None
        self.parent_id: Optional[str] = None
        self.next_sibling_id: Optional[str] = None
        self._save_state()
        
    def _save_state(self) -> None:
        """保存节点状态用于撤销"""
        node = self.document.get_node_by_id(self.node_id)
        if node and node.parent:
            self.parent_id = node.parent.id
            siblings = node.parent.children
            idx = siblings.index(node)
            if idx + 1 < len(siblings):
                self.next_sibling_id = siblings[idx + 1].id
                
    def execute(self) -> bool:
        try:
            node = self.document.get_node_by_id(self.node_id)
            if not node:
                print(f"错误：未找到节点 '{self.node_id}'")
                return False
                
            self.deleted_node = node
            self.document.delete_node(self.node_id)
            return True
        except InvalidNodeError as e:
            print(f"错误：{str(e)}")
            return False
        
    def undo(self) -> bool:
        if not self.deleted_node or not self.parent_id:
            return False
            
        try:
            if self.next_sibling_id:
                self.document.insert_node(self.deleted_node, self.next_sibling_id)
            else:
                self.document.append_node(self.deleted_node, self.parent_id)
            return True
        except (InvalidNodeError, DuplicateIdError):
            return False
            
    @property
    def can_undo(self) -> bool:
        return self.deleted_node is not None and self.parent_id is not None

class EditIdCommand(EditCommand):
    """修改节点ID的命令"""
    
    def __init__(self, document: HTMLDocument, old_id: str, new_id: str):
        """
        初始化ID编辑命令
        
        Args:
            document: 目标HTML文档对象
            old_id: 节点当前的ID
            new_id: 要修改成的新ID
            
        Note:
            - new_id在整个文档中必须唯一
            - 如果节点不存在或新ID已存在，修改将失败
            - ID修改会影响所有引用该节点的操作
        """
        super().__init__(document)
        self.old_id = old_id
        self.new_id = new_id
        
    def execute(self) -> bool:
        try:
            # 先检查节点是否存在
            node = self.document.get_node_by_id(self.old_id)
            if not node:
                print(f"错误：未找到节点 '{self.old_id}'")
                return False
                
            self.document.edit_node_id(self.old_id, self.new_id)
            return True
        except InvalidNodeError as e:
            print(f"错误：{str(e)}")
            return False
        except DuplicateIdError as e:
            print(f"错误：{str(e)}")
            return False
            
    def undo(self) -> bool:
        try:
            self.document.edit_node_id(self.new_id, self.old_id)
            return True
        except (InvalidNodeError, DuplicateIdError):
            return False
            
    @property
    def can_undo(self) -> bool:
        return True

class EditTextCommand(EditCommand):
    """修改节点文本内容的命令"""
    
    def __init__(self, document: HTMLDocument, node_id: str, new_text: str):
        """
        初始化文本编辑命令
        
        Args:
            document: 目标HTML文档对象
            node_id: 要修改的节点ID
            new_text: 新的文本内容
            
        Note:
            - 只能修改节点的直接文本内容
            - 会保存原文本内容用于撤销
            - 如果节点不存在，修改将失败
        """
        super().__init__(document)
        self.node_id = node_id
        self.new_text = new_text
        self.old_text: Optional[str] = None
        self._save_old_text()
        
    def _save_old_text(self) -> None:
        """保存原文本内容用于撤销"""
        node = self.document.get_node_by_id(self.node_id)
        if node:
            self.old_text = node.text
            
    def execute(self) -> bool:
        try:
            # 先检查节点是否存在
            node = self.document.get_node_by_id(self.node_id)
            if not node:
                print(f"错误：未找到节点 '{self.node_id}'")
                return False
                
            self.document.edit_node_text(self.node_id, self.new_text)
            return True
        except InvalidNodeError as e:
            print(f"错误：{str(e)}")
            return False
            
    def undo(self) -> bool:
        if self.old_text is not None:
            try:
                self.document.edit_node_text(self.node_id, self.old_text)
                return True
            except InvalidNodeError:
                return False
        return False
        
    @property
    def can_undo(self) -> bool:
        return self.old_text is not None 