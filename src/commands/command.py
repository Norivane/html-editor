from abc import ABC, abstractmethod
from typing import Optional
from ..models.html_document import HTMLDocument

class Command(ABC):
    """命令基类，定义命令接口"""
    
    def execute(self) -> bool:
        """
        执行命令
        
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        raise NotImplementedError
    
    def undo(self) -> bool:
        """
        撤销命令
        
        Returns:
            bool: 撤销成功返回True，失败返回False
        """
        raise NotImplementedError
    
    @property
    def can_undo(self) -> bool:
        """
        检查命令是否可以撤销
        
        Returns:
            bool: 可以撤销返回True，否则返回False
        """
        raise NotImplementedError