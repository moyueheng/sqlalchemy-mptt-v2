import pytest
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mptt_2 import BaseNestedSets

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

def test_insert_node(session):
    root = Category(name='Root')
    child1 = Category(name='Child 1')
    child2 = Category(name='Child 2')
    
    session.add(root)
    session.commit()
    
    root.insert(0, child1)
    root.insert(1, child2)
    session.commit()
    
    assert len(root.children) == 2
    assert root.children[0] == child1
    assert root.children[1] == child2

def test_is_leaf(session):
    root = Category(name='Root')
    child = Category(name='Child')
    
    session.add_all([root, child])
    session.commit()
    
    root.append(child)
    session.commit()
    
    assert not root.is_leaf
    assert child.is_leaf

def test_is_root(session):
    root = Category(name='Root')
    child = Category(name='Child')
    
    session.add_all([root, child])
    session.commit()
    
    root.append(child)
    session.commit()
    
    assert root.is_root
    assert not child.is_root
