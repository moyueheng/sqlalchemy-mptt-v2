import pytest
from sqlalchemy import String, create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, sessionmaker

from sqlalchemy_mptt_2 import MPTTMixin, MPTTQuery

Base = declarative_base()


class Category(Base, MPTTMixin):
    __tablename__ = "categories"
    name: Mapped[str] = mapped_column(String(64))

    @classmethod
    def query(cls, session):
        return MPTTQuery(cls, session)


@pytest.fixture(scope="function")
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_tree(session):
    root = Category(name="Root")
    session.add(root)
    session.flush()

    child1 = root.add_child(name="Child 1")
    child2 = root.add_child(name="Child 2")
    grandchild = child1.add_child(name="Grandchild")
    session.commit()

    assert root.tree_id == 1
    assert root.level == 0
    assert root.lft == 1
    assert root.rgt == 8
    assert child1.level == 1
    assert child1.lft == 2
    assert child1.rgt == 5
    assert child2.level == 1
    assert child2.lft == 6
    assert child2.rgt == 7
    assert grandchild.level == 2
    assert grandchild.lft == 3
    assert grandchild.rgt == 4
    assert root.parent is None
    assert child1.parent == root
    assert child2.parent == root
    assert grandchild.parent == child1

    # 测试查询方法
    roots = Category.query(session).roots().all()
    assert len(roots) == 1
    assert roots[0] == root

    leaves = Category.query(session).leaves().all()
    assert len(leaves) == 2
    assert set(leaves) == {child2, grandchild}

    tree = Category.query(session).get_tree().all()
    assert len(tree) == 4
    assert tree == [root, child1, grandchild, child2]
