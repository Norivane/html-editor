from typing import List, Set
from pathlib import Path
from .tree_printer import DirectoryPrinter

class DirectoryViewer:
    """目录显示工具类"""
    
    @staticmethod
    def get_tree_view(directory: Path, open_files: Set[str], active_file: str = None) -> str:
        """
        生成目录的树形视图
        
        Args:
            directory: 目录路径
            open_files: 当前打开的文件集合
            active_file: 当前活动的文件
            
        Returns:
            树形格式的目录字符串
        """
        printer = DirectoryPrinter(open_files, active_file)
        return printer.get_tree_view(directory)
    
    @staticmethod
    def get_indented_view(directory: Path, open_files: Set[str], 
                         active_file: str = None, indent: int = 2) -> str:
        """
        生成目录的缩进视图
        
        Args:
            directory: 目录路径
            open_files: 当前打开的文件集合
            active_file: 当前活动的文件
            indent: 缩进空格数
            
        Returns:
            缩进格式的目录字符串
        """
        printer = DirectoryPrinter(open_files, active_file)
        return printer.get_indented_view(directory, indent) 