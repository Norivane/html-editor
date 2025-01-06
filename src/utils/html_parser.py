from typing import Optional, Tuple, Dict, List, Any
from bs4 import BeautifulSoup, Tag
from ..models.html_document import HTMLDocument
from ..models.html_node import HTMLNode
from ..exceptions.editor_exceptions import InvalidNodeError
from .tree_printer import HTMLPrinter

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
        printer = HTMLPrinter()
        return printer.get_indented_view(document.root, indent)
        
    @staticmethod
    def to_tree_string(document: HTMLDocument, show_id: bool = True, 
                      spell_errors: Dict[str, List[Dict[str, Any]]] = None) -> str:
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
        printer = HTMLPrinter(show_id, spell_errors)
        return printer.get_tree_view(document.root) 