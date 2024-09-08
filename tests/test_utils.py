import pytest
from sqlalchemy_mptt_2.utils import ClassNotRegistered, get_tree_table, register_tree

class DummyClass:
    pass

def test_register_tree():
    register_tree(DummyClass)
    assert DummyClass in get_tree_table()

def test_get_tree_table():
    register_tree(DummyClass)
    tree_table = get_tree_table()
    assert isinstance(tree_table, dict)
    assert DummyClass in tree_table

def test_class_not_registered():
    class UnregisteredClass:
        pass

    with pytest.raises(ClassNotRegistered):
        get_tree_table()[UnregisteredClass]
