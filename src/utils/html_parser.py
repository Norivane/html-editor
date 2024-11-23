from typing import Optional, Tuple, Dict, List, Any
from bs4 import BeautifulSoup, Tag
from ..models.html_document import HTMLDocument
from ..models.html_node import HTMLNode
from ..exceptions.editor_exceptions import InvalidNodeError

class HTMLParser:
    """HTML解析工具类，负责HTML字符串和HTMLDocument对象之间的转换"""
    
    @staticmethod
    def parse_html(html_content: str) -> HTMLDocument:
        """
        将HTML字符串解析为HTMLDocument对象
        
        Args:
            html_content: HTML字符串内容
            
        Returns:
            HTMLDocument对象
            
        Raises:
            InvalidNodeError: 当HTML结构无效时抛出
        """
        # 使用lxml解析器解析HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 确保有html标签
        html_tag = soup.find('html')
        if not html_tag:
            raise InvalidNodeError("HTML文档必须包含html根标签")
            
        document = HTMLDocument()
        document.root = HTMLParser._parse_node(html_tag)
        
        # 验证文档结构
        document.validate()
        document.set_unmodified()
        document._update_id_map()
        
        return document
        
    @staticmethod
    def _parse_node(bs_tag: Tag) -> HTMLNode:
        """
        递归解析BeautifulSoup标签为HTMLNode对象
        
        Args:
            bs_tag: BeautifulSoup的Tag对象
            
        Returns:
            HTMLNode对象
        """
        # 获取标签名
        tag_name = bs_tag.name
        
        # 获取ID属性
        node_id = bs_tag.get('id')
        
        # 如果是必需标签且没有指定ID，则使用标签名作为ID
        if tag_name in HTMLNode.REQUIRED_TAGS and not node_id:
            node_id = tag_name
        
        # 提取直接文本内容（不包括子标签中的文本）
        text_content = HTMLParser._extract_direct_text(bs_tag)
        
        # 创建节点
        node = HTMLNode(tag_name, node_id, text_content)
        
        # 递归处理子节点
        for child in bs_tag.children:
            if isinstance(child, Tag):
                child_node = HTMLParser._parse_node(child)
                node.add_child(child_node)
                
        return node
        
    @staticmethod
    def _extract_direct_text(tag: Tag) -> str:
        """
        提取标签的直接文本内容（不包括子标签中的文本）
        
        Args:
            tag: BeautifulSoup的Tag对象
            
        Returns:
            直接文本内容
        """
        return ''.join(child.strip() for child in tag.strings 
                      if child.parent == tag and child.strip())
        
    @staticmethod
    def to_html_string(document: HTMLDocument, indent: int = 2) -> str:
        """
        将HTMLDocument对象转换为格式化的HTML字符串
        
        Args:
            document: HTMLDocument对象
            indent: 缩进空格数
            
        Returns:
            格式化的HTML字符串
        """
        if not document.root:
            return ""
            
        return HTMLParser._node_to_html(document.root, indent)
        
    @staticmethod
    def _node_to_html(node: HTMLNode, indent: int = 2, level: int = 0) -> str:
        """
        递归将节点转换为HTML字符串
        
        Args:
            node: HTMLNode对象
            indent: 缩进空格数
            level: 当前缩进级别
            
        Returns:
            格式化的HTML字符串
        """
        # 计算当前缩进
        current_indent = " " * (level * indent)
        
        # 构建开始标签
        if node.id and node.id != node.tag:
            tag_start = f'<{node.tag} id="{node.id}">'
        else:
            tag_start = f'<{node.tag}>'
            
        # 如果没有子节点和文本，使用简单格式
        if not node.children and not node.text:
            return f"{current_indent}{tag_start}</{node.tag}>\n"
            
        # 构建完整的节点字符串
        result = [f"{current_indent}{tag_start}"]
        
        # 添加文本内容（如果有）
        if node.text:
            result.append(node.text)
            
        # 添加子节点
        if node.children:
            result.append("\n")
            for child in node.children:
                result.append(HTMLParser._node_to_html(child, indent, level + 1))
            result.append(current_indent)
            
        # 添加结束标签
        result.append(f"</{node.tag}>\n")
        
        return "".join(result)
        
    @staticmethod
    def to_tree_string(document: HTMLDocument, show_id: bool = True, spell_errors: Dict[str, List[Dict[str, Any]]] = None) -> str:
        """
        将HTMLDocument对象转换为树形格式的字符串
        
        Args:
            document: HTMLDocument对象
            show_id: 是否显示节点ID
            spell_errors: 拼写检查错误字典
            
        Returns:
            树形格式的字符串
        """
        if not document.root:
            return ""
        
        lines = []
        root = document.root
        
        # 构建根节点文本
        node_text = HTMLParser._build_node_text(root, show_id, spell_errors)
        lines.append(f"{node_text}\n")
        
        # 处理根节点的文本内容
        if root.text:
            lines.append(f"└── {root.text}\n")
        
        # 处理子节点
        for i, child in enumerate(root.children):
            is_last_child = (i == len(root.children) - 1)
            HTMLParser._node_to_tree(child, "", is_last_child, lines, show_id, spell_errors)
        
        return "".join(lines)
        
    @staticmethod
    def _build_node_text(node: HTMLNode, show_id: bool, spell_errors: Dict[str, List[Dict[str, Any]]] = None) -> str:
        """
        构建节点显示文本
        
        Args:
            node: HTMLNode对象
            show_id: 是否显示节点ID
            spell_errors: 拼写检查错误字典
            
        Returns:
            格式化后的节点显示文本
        """
        node_text = node.tag
        if spell_errors and node.id in spell_errors:
            node_text = f"[X] {node_text}"
        if show_id and node.id != node.tag:
            node_text += f"#{node.id}"
        return node_text
        
    @staticmethod
    def _node_to_tree(node: HTMLNode, prefix: str, is_last: bool, 
                      lines: list, show_id: bool, spell_errors: Dict[str, List[Dict[str, Any]]] = None) -> None:
        """
        递归将节点转换为树形格式
        
        Args:
            node: HTMLNode对象
            prefix: 当前行的前缀
            is_last: 是否是最后一个节点
            lines: 用于收集输出行的列表
            show_id: 是否显示节点ID
            spell_errors: 拼写检查错误字典
        """
        connector = "└── " if is_last else "├── "
        
        # 构建节点显示文本
        node_text = HTMLParser._build_node_text(node, show_id, spell_errors)
        lines.append(f"{prefix}{connector}{node_text}\n")
        
        # 准备子节点的前缀
        child_prefix = prefix + ("    " if is_last else "│   ")
        
        # 处理文本内容
        if node.text:
            text_connector = "└── " if not node.children else "├── "
            lines.append(f"{child_prefix}{text_connector}{node.text}\n")
        
        # 处理子节点
        for i, child in enumerate(node.children):
            is_last_child = (i == len(node.children) - 1)
            HTMLParser._node_to_tree(child, child_prefix, is_last_child, lines, show_id, spell_errors) 