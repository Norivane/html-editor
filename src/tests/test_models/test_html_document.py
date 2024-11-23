import pytest
from src.models.html_document import HTMLDocument
from src.models.html_node import HTMLNode
from src.exceptions.editor_exceptions import DuplicateIdError, InvalidNodeError

class TestHTMLDocument:
    @pytest.fixture
    def empty_document(self):
        """创建空文档"""
        return HTMLDocument()

    @pytest.fixture
    def sample_document(self):
        """创建示例文档"""
        doc = HTMLDocument()
        doc.create_empty_document()
        return doc

    def test_create_empty_document(self, empty_document):
        """测试创建空文档"""
        empty_document.create_empty_document()
        
        assert empty_document.root is not None
        assert empty_document.root.tag == 'html'
        assert len(empty_document.root.children) == 2
        
        head = empty_document.root.children[0]
        assert head.tag == 'head'
        assert head.children[0].tag == 'title'
        
        body = empty_document.root.children[1]
        assert body.tag == 'body'

    def test_update_id_map(self, sample_document):
        """测试ID映射更新"""
        # 添加一些节点
        body = sample_document.root.find_by_id('body')
        div = HTMLNode('div', 'test-div')
        body.add_child(div)
        
        sample_document._update_id_map()
        assert 'test-div' in sample_document._id_map
        assert sample_document._id_map['test-div'] == div

    def test_duplicate_id_detection(self, sample_document):
        """测试重复ID检测"""
        body = sample_document.root.find_by_id('body')
        
        # 添加第一个节点
        div1 = HTMLNode('div', 'test-id')
        body.add_child(div1)
        sample_document._update_id_map()
        
        # 添加具有相同ID的第二个节点
        div2 = HTMLNode('div', 'test-id')
        with pytest.raises(DuplicateIdError):
            body.add_child(div2)
            sample_document._update_id_map()

    def test_required_tags_same_id(self, sample_document):
        """测试必需标签使用相同ID"""
        # html和head标签使用标签名作为ID是允许的
        assert sample_document.root.id == 'html'
        assert sample_document.root.children[0].id == 'head'
        sample_document._update_id_map()  # 不应抛出异常

    def test_document_validation(self, empty_document):
        """测试文档验证"""
        # 创建无效的文档结构
        root = HTMLNode('div', 'root')  # 不是html根节点
        empty_document.root = root
        
        with pytest.raises(InvalidNodeError):
            empty_document.validate() 

    def test_modified_flag(self, sample_document):
        """测试文档修改标志"""
        assert not sample_document.is_modified
        
        # 修改节点文本
        sample_document.edit_node_text('body', 'New text')
        assert sample_document.is_modified
        
        # 重置修改标志
        sample_document._modified = False
        assert not sample_document.is_modified

    def test_get_node_by_id_nonexistent(self, sample_document):
        """测试获取不存在的节点"""
        assert sample_document.get_node_by_id('nonexistent') is None