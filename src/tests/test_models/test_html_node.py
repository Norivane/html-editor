import pytest
from src.models.html_node import HTMLNode
from src.exceptions.editor_exceptions import InvalidNodeError

class TestHTMLNode:
    def test_init_required_tag(self):
        """测试必需标签的初始化"""
        node = HTMLNode('html')
        assert node.tag == 'html'
        assert node.id == 'html'
        assert node.text == ''
        assert node.parent is None
        assert node.children == []

    def test_init_with_custom_id(self):
        """测试带自定义ID的初始化"""
        node = HTMLNode('div', 'custom-id', 'some text')
        assert node.tag == 'div'
        assert node.id == 'custom-id'
        assert node.text == 'some text'

    def test_init_non_required_tag_without_id(self):
        """测试非必需标签没有ID时应抛出异常"""
        with pytest.raises(InvalidNodeError):
            HTMLNode('div')

    def test_add_child(self):
        """测试添加子节点"""
        parent = HTMLNode('div', 'parent')
        child = HTMLNode('p', 'child')
        parent.add_child(child)
        
        assert child in parent.children
        assert child.parent == parent
        assert len(parent.children) == 1

    def test_remove_child(self):
        """测试移除子节点"""
        parent = HTMLNode('div', 'parent')
        child = HTMLNode('p', 'child')
        parent.add_child(child)
        parent.remove_child(child)
        
        assert child not in parent.children
        assert child.parent is None
        assert len(parent.children) == 0

    def test_find_by_id(self):
        """测试通过ID查找节点"""
        root = HTMLNode('div', 'root')
        child1 = HTMLNode('p', 'child1')
        child2 = HTMLNode('span', 'child2')
        root.add_child(child1)
        child1.add_child(child2)

        assert root.find_by_id('child2') == child2
        assert root.find_by_id('nonexistent') is None

    def test_to_dict(self):
        """测试节点转换为字典"""
        node = HTMLNode('div', 'test-id', 'test text')
        child = HTMLNode('p', 'child-id')
        node.add_child(child)

        dict_result = node.to_dict()
        assert dict_result['tag'] == 'div'
        assert dict_result['id'] == 'test-id'
        assert dict_result['text'] == 'test text'
        assert len(dict_result['children']) == 1
        assert dict_result['children'][0]['id'] == 'child-id'

    def test_validate(self):
        """测试节点验证"""
        # 测试有效的结构
        root = HTMLNode('html')
        head = HTMLNode('head')
        title = HTMLNode('title')
        root.add_child(head)
        head.add_child(title)
        root.validate()  # 不应抛出异常

        # 测试无效的结构
        with pytest.raises(InvalidNodeError):
            invalid_node = HTMLNode('div')  # 非必需标签没有ID 