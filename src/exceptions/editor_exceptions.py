class EditorException(Exception):
    """编辑器基础异常类"""
    pass

class DuplicateIdError(EditorException):
    """ID重复异常"""
    pass

class InvalidNodeError(EditorException):
    """无效节点异常"""
    pass

class FileOperationError(EditorException):
    """文件操作异常"""
    pass 