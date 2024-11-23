from typing import Optional, Dict, Set, List
from .html_node import HTMLNode
from ..exceptions.editor_exceptions import DuplicateIdError, InvalidNodeError

class HTMLDocument:
    """HTML文档类，用于管理整个HTML文档的结构和操作"""
    
    def __init__(self):
        """初始化HTML文档"""
        self.root: Optional[HTMLNode] = None
        self._id_map: Dict[str, HTMLNode] = {}  # 用于快速查找节点的ID映射
        self._modified: bool = False  # 文档是否被修改的标志
        
    def create_empty_document(self) -> None:
        """
        创建一个空的HTML文档模板
        
        创建基本的HTML结构：
        <html>
          <head>
            <title></title>
          </head>
          <body></body>
        </html>
        """
        html_node = HTMLNode('html')
        head_node = HTMLNode('head')
        title_node = HTMLNode('title')
        body_node = HTMLNode('body')
        
        self.root = html_node
        html_node.add_child(head_node)
        head_node.add_child(title_node)
        html_node.add_child(body_node)
        
        # 更新ID映射
        self._update_id_map()
        self._modified = False
        
    def _update_id_map(self) -> None:
        """更新整个文档的ID映射"""
        self._id_map.clear()
        if self.root:
            self._build_id_map(self.root)
            
    def _build_id_map(self, node: HTMLNode) -> None:
        """
        递归构建ID映射
        
        Args:
            node: 当前处理的节点
            
        Raises:
            DuplicateIdError: 当发现重复ID时抛出
        """
        if node.id in self._id_map:
            existing_node = self._id_map[node.id]
            # 如果是必需标签，且ID等于标签名，则允许重复
            if (node.tag in HTMLNode.REQUIRED_TAGS and 
                node.id == node.tag):
                # 对于必需标签，允许使用标签名作为ID
                pass
            # 如果两个节点都不是必需标签，且ID相同，则报错
            elif (node.tag not in HTMLNode.REQUIRED_TAGS and 
                  existing_node.tag not in HTMLNode.REQUIRED_TAGS):
                raise DuplicateIdError(f"发现重复的ID: {node.id}")
        
        self._id_map[node.id] = node
        
        for child in node.children:
            self._build_id_map(child)
            
    def get_node_by_id(self, id_: str) -> Optional[HTMLNode]:
        """
        通过ID获取节点
        
        Args:
            id_: 节点ID
            
        Returns:
            找到的节点，如果未找到则返回None
        """
        return self._id_map.get(id_)
        
    def insert_node(self, new_node: HTMLNode, insert_location: str) -> None:
        """
        在指定节点之前插入新节点
        
        Args:
            new_node: 要插入的新节点
            insert_location: 目标位置节点的ID
            
        Raises:
            InvalidNodeError: 当目标节点不存在或新节点无效时抛出
            DuplicateIdError: 当新节点ID已存在时抛出
        """
        # 验证新节点
        new_node.validate()
        
        # 检查新节点ID是否已存在
        if new_node.id in self._id_map:
            existing_node = self._id_map[new_node.id]
            # 只有当两个节点都不是必需标签，或者它们的标签名不同时，才视为重复ID
            if (new_node.tag not in HTMLNode.REQUIRED_TAGS or 
                existing_node.tag not in HTMLNode.REQUIRED_TAGS or
                new_node.tag != existing_node.tag):
                raise DuplicateIdError(f"ID '{new_node.id}' 已存在")
        
        # 获取目标节点
        target_node = self.get_node_by_id(insert_location)
        if not target_node:
            raise InvalidNodeError(f"未找到ID为 '{insert_location}' 的节点")
        
        # 获取父节点
        parent_node = target_node.parent
        if not parent_node:
            raise InvalidNodeError(f"目标节点 '{insert_location}' 没有父节点")
        
        # 在目标位置插入新节点
        try:
            index = parent_node.children.index(target_node)
            parent_node.children.insert(index, new_node)
            new_node.parent = parent_node
            self._id_map[new_node.id] = new_node
            self._modified = True
        except ValueError:
            raise InvalidNodeError(f"无法在节点树中找到目标节点 '{insert_location}'")
        
    def append_node(self, new_node: HTMLNode, parent_id: str) -> None:
        """
        将新节点添加为父节点的最后一个子节点
        
        Args:
            new_node: 要添加的新节点
            parent_id: 父节点的ID
            
        Raises:
            InvalidNodeError: 当父节点不存在时抛出
            DuplicateIdError: 当新节点ID已存在时抛出
        """
        # 检查新节点ID是否已存在
        if new_node.id in self._id_map:
            existing_node = self._id_map[new_node.id]
            # 只有当两个节点都不是必需标签，或者它们的标签名不同时，才视为重复ID
            if (new_node.tag not in HTMLNode.REQUIRED_TAGS or 
                existing_node.tag not in HTMLNode.REQUIRED_TAGS or
                new_node.tag != existing_node.tag):
                raise DuplicateIdError(f"ID '{new_node.id}' 已存在")
            
        parent_node = self.get_node_by_id(parent_id)
        if not parent_node:
            raise InvalidNodeError(f"未找到ID为 '{parent_id}' 的节点")
            
        parent_node.add_child(new_node)
        self._id_map[new_node.id] = new_node
        self._modified = True
        
    def delete_node(self, node_id: str) -> None:
        """
        删除指定ID的节点
        
        Args:
            node_id: 要删除的节点ID
            
        Raises:
            InvalidNodeError: 当节点不存在或不能删除时抛出
        """
        node = self.get_node_by_id(node_id)
        if not node:
            raise InvalidNodeError(f"未找到ID为 '{node_id}' 的节点")
            
        # 检查是否是必需的标签
        if node.tag in {'html', 'head', 'title', 'body'}:
            raise InvalidNodeError(f"不能删除必需的标签: {node.tag}")
            
        if node.parent:
            node.parent.remove_child(node)
            self._remove_node_from_id_map(node)
            self._modified = True
            
    def _remove_node_from_id_map(self, node: HTMLNode) -> None:
        """
        从ID映射中递归删除节点及其子节点
        
        Args:
            node: 要删除的节点
        """
        self._id_map.pop(node.id, None)
        for child in node.children:
            self._remove_node_from_id_map(child)
            
    def edit_node_id(self, old_id: str, new_id: str) -> None:
        """
        修改节点的ID
        
        Args:
            old_id: 原ID
            new_id: 新ID
            
        Raises:
            InvalidNodeError: 当节点不存在时抛出
            DuplicateIdError: 当新ID已存在时抛出
        """
        if new_id in self._id_map:
            raise DuplicateIdError(f"ID '{new_id}' 已存在")
            
        node = self.get_node_by_id(old_id)
        if not node:
            raise InvalidNodeError(f"未找到ID为 '{old_id}' 的节点")
            
        del self._id_map[old_id]
        node.id = new_id
        self._id_map[new_id] = node
        self._modified = True
        
    def edit_node_text(self, node_id: str, new_text: str) -> None:
        """
        修改节点的文本内容
        
        Args:
            node_id: 节点ID
            new_text: 新的文本内容
            
        Raises:
            InvalidNodeError: 当节点不存在时抛出
            
        Note:
            - 修改文本内容会设置文档的修改标志
            - 只修改节点的直接文本内容，不影响子节点
        """
        node = self.get_node_by_id(node_id)
        if not node:
            raise InvalidNodeError(f"未找到ID为 '{node_id}' 的节点")
            
        node.text = new_text
        self._modified = True
        
    @property
    def is_modified(self) -> bool:
        """
        获取文档是否被修改的状态
        
        Returns:
            如果文档被修改返回True，否则返回False
        """
        return self._modified
        
    def set_unmodified(self) -> None:
        """将文档标记为未修改状态"""
        self._modified = False
        
    def validate(self) -> None:
        """
        验证整个文档的有效性
        
        Raises:
            InvalidNodeError: 当文档结构无效时抛出
        """
        if not self.root or self.root.tag != 'html':
            raise InvalidNodeError("文档必须有一个html根节点")
            
        # 验证必需的结构
        head = None
        body = None
        title = None
        
        for child in self.root.children:
            if child.tag == 'head':
                head = child
            elif child.tag == 'body':
                body = child
                
        if not head or not body:
            raise InvalidNodeError("html节点必须包含head和body子节点")
            
        for child in head.children:
            if child.tag == 'title':
                title = child
                break
                
        if not title:
            raise InvalidNodeError("head节点必须包含title子节点") 
        
    def set_root(self, root: HTMLNode) -> None:
        """
        设置文档根节点并更新ID映射
        
        Args:
            root: 根节点
        """
        self.root = root
        self._update_id_map()
        self._modified = False