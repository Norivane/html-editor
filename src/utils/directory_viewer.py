from typing import List, Set
from pathlib import Path

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
        lines = []
        
        # 直接添加根目录名称，不带连接符
        display_name = directory.name
        lines.append(f"{display_name}\n")
        
        # 获取并排序子项目
        entries = sorted(list(directory.iterdir()),
                        key=lambda p: (p.is_file(), p.name))
        
        # 过滤掉隐藏文件和特定文件
        entries = [e for e in entries if not e.name.startswith('.') 
                  and e.name != 'session.json']
        
        # 递归处理子项目
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            DirectoryViewer._build_tree(directory, entry, "", is_last, 
                                      lines, open_files, active_file)
        
        return "".join(lines)
    
    @staticmethod
    def _build_tree(base_path: Path, current_path: Path, prefix: str, 
                    is_last: bool, lines: List[str], open_files: Set[str], 
                    active_file: str) -> None:
        """
        递归构建目录树
        
        Args:
            base_path: 基础路径
            current_path: 当前路径
            prefix: 当前行的前缀
            is_last: 是否是最后一个项目
            lines: 用于收集输出行的列表
            open_files: 当前打开的文件集合
            active_file: 当前活动的文件
        """
        # 确定当前行的连接符
        connector = "└── " if is_last else "├── "
        rel_path = str(current_path.relative_to(base_path))
        
        # 构建显示名称
        display_name = DirectoryViewer._build_display_name(
            current_path, rel_path, active_file, open_files)
        
        # 添加当前行
        lines.append(f"{prefix}{connector}{display_name}\n")
        
        # 处理子项目
        if current_path.is_dir():
            entries = DirectoryViewer._get_sorted_entries(current_path)
            
            for i, entry in enumerate(entries):
                is_last_entry = (i == len(entries) - 1)
                new_prefix = prefix + ("    " if is_last else "│   ")
                DirectoryViewer._build_tree(base_path, entry, new_prefix, 
                                         is_last_entry, lines, open_files, 
                                         active_file)
    
    @staticmethod
    def _build_display_name(path: Path, rel_path: str, active_file: str, open_files: Set[str]) -> str:
        """
        构建显示名称
        
        Args:
            path: 文件或目录路径
            rel_path: 相对于基础路径的路径
            active_file: 当前活动的文件
            open_files: 当前打开的文件集合
            
        Returns:
            格式化后的显示名称
        """
        display_name = path.name
        if path.is_file():
            if rel_path == active_file:
                display_name = f"> {display_name}"
            if rel_path in open_files:
                display_name = f"{display_name} *"
        return display_name
    
    @staticmethod
    def _get_sorted_entries(directory: Path) -> List[Path]:
        """
        获取排序后的目录条目
        
        Args:
            directory: 目录路径
            
        Returns:
            排序后的路径列表，不包含隐藏文件和特定文件
        """
        entries = sorted(list(directory.iterdir()),
                        key=lambda p: (p.is_file(), p.name))
        return [e for e in entries if not e.name.startswith('.')
                and e.name != 'session.json']
    
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
        lines = []
        DirectoryViewer._build_indent(directory, directory, 0, indent, lines, 
                                    open_files, active_file)
        return "".join(lines)
    
    @staticmethod
    def _build_indent(base_path: Path, current_path: Path, level: int, 
                     indent: int, lines: List[str], open_files: Set[str], 
                     active_file: str) -> None:
        """
        递归构建缩进目录
        
        Args:
            base_path: 基础路径
            current_path: 当前路径
            level: 当前缩进级别
            indent: 缩进空格数
            lines: 用于收集输出行的列表
            open_files: 当前打开的文件集合
            active_file: 当前活动的文件
        """
        # 计算当前缩进
        current_indent = " " * (level * indent)
        
        # 获取相对路径
        rel_path = str(current_path.relative_to(base_path))
        
        # 构建显示名称
        display_name = current_path.name
        if current_path.is_file():
            if rel_path == active_file:
                display_name = f"> {display_name}"
            if rel_path in open_files:
                display_name = f"{display_name} *"
        
        # 添加当前行
        lines.append(f"{current_indent}{display_name}\n")
        
        # 处理子项目
        if current_path.is_dir():
            entries = sorted(list(current_path.iterdir()),
                           key=lambda p: (p.is_file(), p.name))
            entries = [e for e in entries if not e.name.startswith('.') 
                      and e.name != 'session.json']
            
            for entry in entries:
                DirectoryViewer._build_indent(base_path, entry, level + 1, 
                                           indent, lines, open_files, active_file) 