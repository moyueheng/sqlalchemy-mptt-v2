from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session


class MPTTManager:
    @staticmethod
    def initialize_root(instance: Any) -> None:
        session = Session.object_session(instance)
        if session is None:
            raise ValueError("Instance is not associated with a session")

        max_tree_id = session.execute(
            select(instance.__class__.tree_id).order_by(instance.__class__.tree_id.desc())
        ).scalar()
        instance.tree_id = (max_tree_id or 0) + 1
        instance.lft = 1
        instance.rgt = 2
        instance.level = 0

    @staticmethod
    def add_child(instance: Any, **kwargs: Any) -> Any:
        session = Session.object_session(instance)
        if session is None:
            raise ValueError("Instance is not associated with a session")

        new_node = instance.__class__(**kwargs)
        right_most = instance.rgt

        session.execute(
            update(instance.__class__)
            .where(instance.__class__.tree_id == instance.tree_id, instance.__class__.rgt >= right_most)
            .values(rgt=instance.__class__.rgt + 2)
        )
        session.execute(
            update(instance.__class__)
            .where(instance.__class__.tree_id == instance.tree_id, instance.__class__.lft > right_most)
            .values(lft=instance.__class__.lft + 2)
        )

        new_node.tree_id = instance.tree_id
        new_node.parent_id = instance.id
        new_node.lft = right_most
        new_node.rgt = right_most + 1
        new_node.level = instance.level + 1

        session.add(new_node)
        session.flush()

        return new_node

    @staticmethod
    def move_node(instance: Any, target: Any, position: str = "last-child") -> None:
        # 实现移动节点的逻辑
        pass
