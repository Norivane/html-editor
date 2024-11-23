# HTML 文档编辑器

一个基于命令行的HTML文档编辑器，支持文档的创建、编辑、保存以及多种显示方式。该编辑器提供了丰富的命令行接口，方便用户进行HTML文档的编辑和管理。

## 功能特点

- 支持创建、加载和保存HTML文档
- 提供树形和缩进两种文档显示方式
- 内置拼写检查功能
- 支持文档编辑操作的撤销和重做
- 多文档管理，支持在多个文件间切换
- 目录树形显示功能

## 命令说明

### 文档操作
- `init <filename>` - 创建新的HTML文档
- `load/read <filename>` - 加载现有HTML文档
- `save [filename]` - 保存当前文档，可选指定新文件名
- `close` - 关闭当前文档
- `edit <filename>` - 切换到指定文档进行编辑

### 编辑命令
- `insert <tagName> <idValue> <insertLocation> [textContent]` - 在指定位置前插入新元素
  - tagName: HTML标签名
  - idValue: 新元素的ID
  - insertLocation: 插入位置的目标元素ID
  - textContent: 可选的文本内容
  
- `append <tagName> <idValue> <parentId> [textContent]` - 将新元素追加为指定父元素的子元素
  - tagName: HTML标签名
  - idValue: 新元素的ID
  - parentId: 父元素的ID
  - textContent: 可选的文本内容

- `delete <nodeId>` - 删除指定ID的元素及其子元素
- `edit-id <oldId> <newId>` - 修改元素的ID
- `edit-text <nodeId> <newText>` - 修改元素的文本内容

### 显示命令
- `print-tree` - 以树形结构显示文档
- `print-indent` - 以缩进方式显示文档
- `spell-check` - 检查文档中的拼写错误

### 目录操作命令
- `dir-tree` - 以树形结构显示当前目录
- `dir-indent` - 以缩进方式显示当前目录

## 安装说明

1. 克隆项目仓库：
   ```bash
   git clone https://github.com/Norivane/html-editor.git
   cd html-editor
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 运行测试

项目使用pytest进行单元测试。运行测试的方法：

1. 安装测试依赖：
   ```bash
   pip install pytest pytest-cov
   ```

2. 运行测试：
   ```bash
   pytest
   ```
   
3. 测试特定文件：
   ```bash
   pytest src/tests/test_editor/test_editor.py  # 测试编辑器模块
   pytest src/tests/test_commands/  # 测试命令模块
   pytest src/tests/test_document/  # 测试文档模块
   ```

4. 运行带覆盖率报告的测试：
   ```bash
   pytest --cov=src src/tests/
   ```

## 简单使用示例

1. 启动编辑器：
   ```bash
   python main.py
   ```

2. 创建新文档：
   ```
   html-editor> init test.html
   ```

3. 添加元素：
   ```
   html-editor> append div main body "Main content"
   html-editor> insert p para1 main "First paragraph"
   ```

4. 查看文档结构：
   ```
   html-editor> print-tree
   ```

5. 保存文档：
   ```
   html-editor> save
   ```
