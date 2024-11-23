from typing import Optional, List, Dict
from ..exceptions.editor_exceptions import DuplicateIdError, InvalidNodeError

class HTMLNode:
    """HTML节点的基类，用于表示HTML文档中的各种元素"""
    
    REQUIRED_TAGS = {'html', 'head', 'title', 'body'}
    
    def __init__(self, tag: str, id_: Optional[str] = None, text: str = ""):
        """
        初始化HTML节点
        
        Args:
            tag: 标签名称
            id_: 节点ID，如果不提供且是必需标签则使用标签名作为默认ID
            text: 节点的文本内容
        """
        self.tag = tag.lower()
        # 对于必需标签，如果没有提供id则使用标签名
        if self.tag in self.REQUIRED_TAGS:
            self.id = id_ if id_ else self.tag
        else:
            # 对于其他标签，必须提供id
            if not id_:
                raise InvalidNodeError(f"非必需标签 '{self.tag}' 必须提供id属性")
            self.id = id_
            
        self.text = text
        self.parent: Optional[HTMLNode] = None
        self.children: List[HTMLNode] = []
        
    def add_child(self, child: 'HTMLNode') -> None:
        """
        添加子节点
        
        Args:
            child: 要添加的子节点
        """
        if child.parent:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        
    def remove_child(self, child: 'HTMLNode') -> None:
        """
        移除子节点
        
        Args:
            child: 要移除的子节点
        """
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            
    def find_by_id(self, id_: str) -> Optional['HTMLNode']:
        """
        通过ID查找节点
        
        Args:
            id_: 要查找的节点ID
            
        Returns:
            找到的节点，如果未找到则返回None
        """
        if self.id == id_:
            return self
            
        for child in self.children:
            result = child.find_by_id(id_)
            if result:
                return result
        return None
        
    def to_dict(self) -> Dict:
        """
        将节点转换为字典格式
        
        Returns:
            包含节点信息的字典
        """
        return {
            'tag': self.tag,
            'id': self.id,
            'text': self.text,
            'children': [child.to_dict() for child in self.children]
        }
        
    def validate(self) -> None:
        """
        验证节点的有效性
        
        Raises:
            InvalidNodeError: 当节点不符合要求时抛出
        """
        # 检查非必需标签是否有ID
        if self.tag not in self.REQUIRED_TAGS and not self.id:
            raise InvalidNodeError(f"非必需标签 '{self.tag}' 必须有ID属性")
            
        # 递归验证子节点
        for child in self.children:
            child.validate()