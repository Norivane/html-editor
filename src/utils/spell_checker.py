from typing import Dict, List, Set, Any
from spellchecker import SpellChecker as PySpellChecker
from ..models.html_document import HTMLDocument
from ..models.html_node import HTMLNode
import re

class SpellChecker:
    """HTML文档拼写检查工具"""
    
    def __init__(self):
        """初始化拼写检查器"""
        self.checker = PySpellChecker()
        self.ignored_words: Set[str] = {
            'div', 'html', 'css', 'js',  # HTML相关术语
            'webpage', 'website', 'online',  # Web相关术语
            'com', 'org', 'net',  # 常见域名后缀
        }
    
    def check_document(self, document: HTMLDocument) -> Dict[str, List[Dict[str, Any]]]:
        """
        检查整个文档的拼写
        
        Args:
            document: HTML文档
            
        Returns:
            错误报告，格式为：{节点ID: [{错误类型, 原文本, 建议修正}]}
        """
        if not document.root:
            return {}
        
        errors = {}
        self._check_node(document.root, errors)
        return errors
    
    def _check_node(self, node: HTMLNode, errors: Dict[str, List[Dict[str, Any]]]) -> None:
        """
        递归检查节点的拼写错误
        
        Args:
            node: HTML节点
            errors: 错误收集字典
        """
        if node.text:
            # 检查节点的文本内容
            text_errors = self._check_text(node.text)
            if text_errors:
                errors[node.id] = text_errors
        
        # 递归检查子节点
        for child in node.children:
            self._check_node(child, errors)
    
    def _check_text(self, text: str) -> List[Dict[str, Any]]:
        """
        检查文本中的拼写错误
        
        Args:
            text: 待检查的文本
            
        Returns:
            错误列表，每个错误包含类型、原文本和建议修正
        """
        # 预处理文本
        text = self._preprocess_text(text)
        sentences = text.split('.')
        errors = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # 分词并过滤特殊字符
            words = [word.strip('.,!?:;()[]{}') for word in sentence.split()]
            words = [word for word in words if word and not word.isdigit()]
            
            # 检查每个单词
            misspelled = set()
            for word in words:
                if word not in self.ignored_words and not self._check_word(word):
                    misspelled.add(word)
            
            if misspelled:
                error_info = {
                    'type': 'spelling',
                    'text': sentence,
                    'misspelled': list(misspelled),
                    'suggestions': {word: self.checker.candidates(word) 
                                  for word in misspelled}
                }
                if error_info['suggestions']:
                    errors.append(error_info)
        
        return errors
    
    def add_ignored_word(self, word: str) -> None:
        """
        添加忽略的单词
        
        Args:
            word: 要忽略的单词
        """
        self.ignored_words.add(word.lower()) 
    
    def remove_ignored_word(self, word: str) -> None:
        """
        移除忽略的单词
        
        Args:
            word: 要移除的单词
        """
        self.ignored_words.remove(word.lower())
    
    def get_ignored_words(self) -> Set[str]:
        """
        获取所有被忽略的单词
        
        Returns:
            被忽略单词的集合
        """
        return self.ignored_words
    
    def _preprocess_text(self, text: str) -> str:
        """
        预处理文本内容
        
        Args:
            text: 要处理的文本
            
        Returns:
            处理后的文本
        """
        # 移除特殊符号（版权符号等）
        text = re.sub(r'[©®™]', '', text)
        # 处理日期格式
        text = re.sub(r'\d{4}-\d{2}-\d{2}', '', text)
        # 移除多余的标点符号
        text = re.sub(r'[.,:;]$', '', text)
        # 保留连字符（因为在_check_word中会处理）
        return text
    
    def _check_word(self, word: str) -> bool:
        """
        递归检查单词拼写是否正确
        
        Args:
            word: 要检查的单词
            
        Returns:
            拼写是否正确
        """
        # 检查是否是复合词（包含连字符）
        if '-' in word:
            return all(self._check_word(part) for part in word.split('-'))
            
        # 检查驼峰命名的复合词（如 MyWebpage）
        elif re.search(r'[A-Z]', word[1:]):
            parts = re.findall('[A-Z][^A-Z]*|[^A-Z]+', word)
            return all(self._check_word(part.lower()) for part in parts)
            
        # 检查普通单词
        return word.lower() in self.ignored_words or not self.checker.unknown([word.lower()])