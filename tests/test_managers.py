import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mptt_2 import BaseNestedSets
from sqlalchemy_mptt_2.managers import TreeManager

Base = declarative_base()

class Category(Base, BaseNestedSets):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

@pytest.fixture(scope="function")
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="function")
def tree_manager(session):
    return TreeManager(Category, session)

def test_get_tree(session, tree_manager):
    root = Category(name='Root')
    child1 = Category(name='Child 1')
    child2 = Category(name='Child 2')
    session.add_all([root, child1, child2])
    session.commit()

    root.append(child1)
    root.append(child2)
    session.commit()

    tree = tree_manager.get_tree()
    assert len(tree) == 3
    assert tree[0].name == 'Root'
    assert len(tree[0].children) == 2

def test_move_node(session, tree_manager):
    root1 = Category(name='Root 1')
    root2 = Category(name='Root 2')
    child = Category(name='Child')
    session.add_all([root1, root2, child])
    session.commit()

    root1.append(child)
    session.commit()

    tree_manager.move_node(child, root2)
    session.commit()

    assert child.parent == root2
    assert child in root2.children
    assert child not in root1.children
