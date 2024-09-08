from typing import Any, Optional

from sqlalchemy import ForeignKey, Index, Integer, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from sqlalchemy_mptt_2.managers import MPTTManager
from sqlalchemy_mptt_2.query import MPTTQuery


class MPTTMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lft: Mapped[int] = mapped_column(Integer, nullable=False)
    rgt: Mapped[int] = mapped_column(Integer, nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    tree_id: Mapped[int] = mapped_column(Integer, nullable=False)

    @declared_attr
    def parent_id(cls) -> Mapped[Optional[int]]:
        return mapped_column(Integer, ForeignKey(f"{cls.__tablename__}.id"), nullable=True)

    @declared_attr
    def parent(cls) -> Mapped[Optional["MPTTMixin"]]:
        return relationship(cls.__name__, remote_side=[cls.id], backref="children")

    @declared_attr
    def __table_args__(cls) -> Any:
        return (
            Index(f"ix_{cls.__tablename__}_lft_rgt", "lft", "rgt"),
            Index(f"ix_{cls.__tablename__}_tree_id_level", "tree_id", "level"),
        )

    @hybrid_property
    def is_root(self) -> bool:
        return self.parent_id is None

    @hybrid_property
    def is_leaf(self) -> bool:
        return self.rgt - self.lft == 1

    def add_child(self, **kwargs) -> "MPTTMixin":
        return MPTTManager.add_child(self, **kwargs)

    def move_to(self, target: "MPTTMixin", position: str = "last-child") -> None:
        MPTTManager.move_node(self, target, position)

    @classmethod
    def query(cls, session):
        return MPTTQuery(cls, session)


@event.listens_for(MPTTMixin, "before_insert", propagate=True)
def before_insert(mapper, connection, instance):
    if instance.parent_id is None:
        from sqlalchemy_mptt_2.managers import MPTTManager

        MPTTManager.initialize_root(instance)
