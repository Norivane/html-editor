#!/usr/bin/env python3
from pathlib import Path
from typing import List, Optional
import sys
import cmd
import shlex
from src.editor.session import Session
from src.utils.directory_viewer import DirectoryViewer
from src.commands.edit_commands import (InsertCommand, AppendCommand, DeleteCommand, EditIdCommand, EditTextCommand)
from src.commands.display_commands import (PrintTreeCommand, PrintIndentCommand, SpellCheckCommand)
from src.exceptions.editor_exceptions import EditorException

class HTMLEditorShell(cmd.Cmd):
    """HTML编辑器的命令行界面"""
    
    intro = '欢迎使用HTML编辑器。输入 help 或 ? 查看帮助。\n'
    prompt = 'html-editor> '
    
    def __init__(self):
        """初始化编辑器shell"""
        super().__init__()
        self.session = Session()
        self.base_dir = Path.cwd()
    
    aliases = {
        "edit-text": "edit_text",   
        "print-indent": "print_indent",
        "spell-check": "spell_check",
        "editor-list": "editor_list",
        "print-tree": "print_tree",
        "edit-id": "edit_id",
        "dir-tree": "dir_tree",
        "dir-indent": "dir_indent"
    }

    def onecmd(self, line):
        """将命令中的 "-" 替换为 "_" """
        cmd = line.split(' ')[0] if ' ' in line else line
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
            if ' ' in line:
                line = f"{cmd} {line.split(' ', 1)[1]}"
            else:
                line = cmd
        return super().onecmd(line)
    
    def preloop(self):
        """命令行启动前的准备工作"""
        if not self.session.active_editor:
            print("提示：使用 load <文件名> 加载文件，或使用 init 创建新文档")
    
    def precmd(self, line: str) -> str:
        """命令执行前的处理"""
        # 如果是空命令，直接返回空字符串
        if not line.strip():
            return ""
        
        # 检查是否有活动编辑器
        if not self.session.active_editor:
            # 允许执行的特殊命令
            if line.startswith(('load ', 'init', 'help', '?', 'quit', 'dir')):
                return line
            print("错误：请先加载或创建文档")
            return ""
        return line
    
    def do_load(self, arg: str) -> None:
        """
        加载HTML文件
        用法: load filename.html
        """
        if not arg:
            print("错误：请指定文件名")
            return
        
        filepath = Path(arg)
        if self.session.load_file(filepath):
            print(f"已加载文件：{filepath}")
        
    def do_read(self, arg: str) -> None:
        """
        读取HTML文件（load命令的别名）
        用法: read <文件名>
        """
        self.do_load(arg)
    
    def do_init(self, arg: str) -> None:
        """
        初始化新的HTML文档
        用法: init [filename.html]
        """
        if not arg:
            print("错误：请指定文件名")
            return
        
        filepath = Path(arg)
        if self.session.create_new_file(filepath):
            print(f"已创建新文档：{filepath}")
    
    def do_save(self, arg: str) -> None:
        """
        保存当前文档
        用法: save [filename.html]
        """
        if not self.session.active_editor:
            return
        
        filepath = Path(arg) if arg else self.session.active_editor.filepath
        try:
            self.session.active_editor.save_file(filepath)
            print(f"文档已保存到：{filepath}")
        except EditorException as e:
            print(f"保存失败：{str(e)}")
    
    def do_close(self, arg: str) -> None:
        """
        关闭当前文档
        用法: close
        """
        if not self.session.active_editor:
            return
        
        filepath = self.session.active_editor.filepath
        if self.session.close_editor(filepath):
            print(f"已关闭文档：{filepath}")
    
    def do_edit(self, arg: str) -> None:
        """
        切换编辑的文档
        用法: edit filename.html
        """
        if not arg:
            print("错误：请指定文件名")
            return
        
        filepath = Path(arg)
        if self.session.switch_editor(filepath):
            print(f"当前编辑：{filepath}")
        else:
            print(f"错误：文件 {filepath} 未打开")
    
    def do_insert(self, arg: str) -> None:
        """
        在指定位置前插入新元素
        用法: insert tagName idValue insertLocation [textContent]
        """
        args = shlex.split(arg)
        if len(args) < 3:
            print("错误：参数不足")
            return
        
        tag_name, id_value, insert_location, *text = args
        text_content = " ".join(text) if text else ""
        
        command = InsertCommand(
            self.session.active_editor.document,
            tag_name, id_value, insert_location, text_content
        )
        if self.session.active_editor.execute_command(command):
            print("插入成功")
        else:
            print("插入失败")
    
    def do_append(self, arg: str) -> None:
        """
        在指定元素内添加子元素
        用法: append tagName idValue parentElement [textContent]
        """
        args = shlex.split(arg)
        if len(args) < 3:
            print("错误：参数不足")
            return
        
        tag_name, id_value, parent_id, *text = args
        text_content = " ".join(text) if text else ""
        
        command = AppendCommand(
            self.session.active_editor.document,
            tag_name, id_value, parent_id, text_content
        )
        if self.session.active_editor.execute_command(command):
            print("添加成功")
        else:
            print("添加失败")
    
    def do_delete(self, arg: str) -> None:
        """
        删除指定元素
        用法: delete elementId
        """
        if not arg:
            print("错误：请指定元素ID")
            return
        
        command = DeleteCommand(self.session.active_editor.document, arg)
        if self.session.active_editor.execute_command(command):
            print("删除成功")
        else:
            print("删除失败")
    
    def do_edit_id(self, arg: str) -> None:
        """
        修改元素ID
        用法: edit-id oldId newId
        """
        args = arg.split()
        if len(args) != 2:
            print("错误：需要旧ID和新ID")
            return
        
        old_id, new_id = args
        command = EditIdCommand(self.session.active_editor.document, old_id, new_id)
        if self.session.active_editor.execute_command(command):
            print("ID修改成功")
        else:
            print("ID修改失败")
    
    def do_edit_text(self, arg: str) -> None:
        """
        修改元素文本
        用法: edit-text elementId [newText]
        """
        args = shlex.split(arg)
        if not args:
            print("错误：请指定元素ID")
            return
        
        element_id, *text = args
        text_content = " ".join(text) if text else ""
        
        command = EditTextCommand(
            self.session.active_editor.document,
            element_id, text_content
        )
        if self.session.active_editor.execute_command(command):
            print("文本修改成功")
        else:
            print("文本修改失败")
    
    def do_print_tree(self, arg: str) -> None:
        """
        以树形格式显示文档
        用法: print-tree
        """
        command = PrintTreeCommand(
            self.session.active_editor.document,
            self.session.active_editor.show_id
        )
        command.execute()
    
    def do_print_indent(self, arg: str) -> None:
        """
        以缩进格式显示文档
        用法: print-indent [indent]
        """
        indent = int(arg) if arg.isdigit() else 2
        command = PrintIndentCommand(
            self.session.active_editor.document,
            indent
        )
        command.execute()
    
    def do_spell_check(self, arg: str) -> None:
        """
        执行拼写检查
        用法: spell-check
        """
        command = SpellCheckCommand(self.session.active_editor.document)
        command.execute()
    
    def do_undo(self, arg: str) -> None:
        """
        撤销上一个操作
        用法: undo
        """
        if self.session.active_editor.undo():
            print("撤销成功")
        else:
            print("没有可撤销的操作")
    
    def do_redo(self, arg: str) -> None:
        """
        重做上一个被撤销的操作
        用法: redo
        """
        if self.session.active_editor.redo():
            print("重做成功")
        else:
            print("没有可重做的操作")
    
    def do_showid(self, arg: str) -> None:
        """
        控制是否显示节点ID
        用法: showid true|false
        """
        if arg.lower() not in ('true', 'false'):
            print("错误：参数必须是 true 或 false")
            return
        
        self.session.active_editor.show_id = (arg.lower() == 'true')
        print(f"ID显示已{'开启' if self.session.active_editor.show_id else '关闭'}")
    
    def do_dir_tree(self, arg: str) -> None:
        """
        以树形结构显示目录
        用法: dir-tree
        """
        try:
            open_files = set()
            active_file = None
            
            for editor in self.session.editors.values():
                try:
                    rel_path = editor.filepath.resolve().relative_to(self.base_dir.resolve())
                    file_str = str(rel_path)
                    open_files.add(file_str)
                    if editor == self.session.active_editor:
                        active_file = file_str
                except ValueError:
                    # 如果文件不在基础目录下，使用完整路径
                    file_str = str(editor.filepath)
                    open_files.add(file_str)
                    if editor == self.session.active_editor:
                        active_file = file_str
            
            print(DirectoryViewer.get_tree_view(
                self.base_dir, open_files, active_file))
        except Exception as e:
            print(f"显示目录时出错：{str(e)}")
    
    def do_dir_indent(self, arg: str) -> None:
        """
        以缩进结构显示目录
        用法: dir-indent
        """
        try:
            open_files = set()
            active_file = None
            
            for editor in self.session.editors.values():
                try:
                    rel_path = editor.filepath.resolve().relative_to(self.base_dir.resolve())
                    file_str = str(rel_path)
                    open_files.add(file_str)
                    if editor == self.session.active_editor:
                        active_file = file_str
                except ValueError:
                    # 如果文件不在基础目录下，使用完整路径
                    file_str = str(editor.filepath)
                    open_files.add(file_str)
                    if editor == self.session.active_editor:
                        active_file = file_str
            
            print(DirectoryViewer.get_indented_view(
                self.base_dir, open_files, active_file))
        except Exception as e:
            print(f"显示目录时出错：{str(e)}")
    def do_editor_list(self, arg: str) -> None:
        """
        显示打开的文件列表
        用法: editor-list
        """
        if not self.session.editors:
            print("没有打开的文件")
            return
        
        for filename, editor in self.session.editors.items():
            prefix = "> " if editor == self.session.active_editor else "  "
            suffix = " *" if editor.is_modified else ""
            print(f"{prefix}{filename}{suffix}")
    
    def do_quit(self, arg: str) -> bool:
        """
        退出编辑器
        用法: quit
        """
        # 检查是否有未保存的文件
        modified_files = [filename for filename, editor in self.session.editors.items()
                         if editor.is_modified]
        
        if modified_files:
            print("以下文件尚未保存：")
            for filename in modified_files:
                print(f"  {filename}")
            response = input("确定要退出吗? (y/n): ")
            if response.lower() != 'y':
                return False
        
        # 保存会话状态
        self.session.save_session()
        print("再见！")
        return True
    
    def default(self, line: str) -> None:
        """处理未知命令"""
        print(f"错误：未知命令 '{line}'")
        print("使用 'help' 查看可用命令")

def main():
    """主程序入口"""
    try:
        HTMLEditorShell().cmdloop()
    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        print(f"发生错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 