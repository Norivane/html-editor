from abc import ABC, abstractmethod
from typing import List, Set, Any, Optional, Dict
from pathlib import Path
from ..models.html_node import HTMLNode

class TreePrinter(ABC):
    """树形结构打印的基类"""
    
    @abstractmethod
    def get_root_name(self, root: Any) -> str:
        """获取根节点显示名称"""
        pass
        
    @abstractmethod
    def get_children(self, node: Any) -> List[Any]:
        """获取节点的子节点列表"""
        pass
        
    @abstractmethod
    def build_display_name(self, node: Any) -> str:
        """构建节点的显示名称"""
        pass
        
    @abstractmethod
    def should_skip_node(self, node: Any) -> bool:
        """判断是否应该跳过该节点"""
        pass

    def get_tree_view(self, root: Any) -> str:
        """生成树形视图"""
        lines = []
        lines.append(f"{self.get_root_name(root)}\n")
        
        children = self.get_children(root)
        for i, child in enumerate(children):
            if self.should_skip_node(child):
                continue
            is_last = (i == len(children) - 1)
            self._build_tree(child, "", is_last, lines)
            
        return "".join(lines)
    
    def _build_tree(self, node: Any, prefix: str, is_last: bool, lines: List[str]) -> None:
        """递归构建树形结构"""
        connector = "└── " if is_last else "├── "
        display_name = self.build_display_name(node)
        lines.append(f"{prefix}{connector}{display_name}\n")
        
        children = self.get_children(node)
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        for i, child in enumerate(children):
            if self.should_skip_node(child):
                continue
            is_last_child = (i == len(children) - 1)
            self._build_tree(child, new_prefix, is_last_child, lines)
            
    def get_indented_view(self, root: Any, indent: int = 2) -> str:
        """生成缩进视图"""
        lines = []
        self._build_indent(root, 0, indent, lines)
        return "".join(lines)
        
    def _build_indent(self, node: Any, level: int, indent: int, lines: List[str]) -> None:
        """递归构建缩进结构"""
        current_indent = " " * (level * indent)
        display_name = self.build_display_name(node)
        lines.append(f"{current_indent}{display_name}\n")
        
        children = self.get_children(node)
        for child in children:
            if self.should_skip_node(child):
                continue
            self._build_indent(child, level + 1, indent, lines)

class DirectoryPrinter(TreePrinter):
    """目录结构打印器"""
    
    def __init__(self, open_files: Set[str], active_file: Optional[str] = None):
        self.open_files = open_files
        self.active_file = active_file
        self.base_path: Optional[Path] = None
        
    def get_root_name(self, root: Path) -> str:
        self.base_path = root
        return root.name
        
    def get_children(self, node: Path) -> List[Path]:
        if not node.is_dir():
            return []
        entries = sorted(list(node.iterdir()),
                        key=lambda p: (p.is_file(), p.name))
        return entries
        
    def build_display_name(self, node: Path) -> str:
        display_name = node.name
        if node.is_file() and self.base_path:
            rel_path = str(node.relative_to(self.base_path))
            if rel_path == self.active_file:
                display_name = f"> {display_name}"
            if rel_path in self.open_files:
                display_name = f"{display_name} *"
        return display_name
        
    def should_skip_node(self, node: Path) -> bool:
        return node.name.startswith('.') or node.name == 'session.json' 

class HTMLPrinter(TreePrinter):
    """HTML文档结构打印器"""
    
    def __init__(self, show_id: bool = True, spell_errors: Optional[Dict[str, List[Dict[str, Any]]]] = None):
        self.show_id = show_id
        self.spell_errors = spell_errors
        
    def get_root_name(self, root: HTMLNode) -> str:
        return self.build_display_name(root)
        
    def get_children(self, node: HTMLNode) -> List[HTMLNode]:
        return node.children
        
    def build_display_name(self, node: HTMLNode) -> str:
        node_text = node.tag
        if self.spell_errors and node.id in self.spell_errors:
            node_text = f"[X] {node_text}"
        if self.show_id and node.id != node.tag:
            node_text += f"#{node.id}"
        return node_text
        
    def should_skip_node(self, node: HTMLNode) -> bool:
        return False 