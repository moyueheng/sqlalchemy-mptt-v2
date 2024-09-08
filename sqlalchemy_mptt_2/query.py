from sqlalchemy.orm import Query


class MPTTQuery(Query):
    def __init__(self, entities, session):
        super().__init__(entities, session)
        self.model_class = self._only_full_mapper_zero("get").class_

    def roots(self):
        return self.filter(self.model_class.parent_id == None)

    def leaves(self):
        return self.filter(self.model_class.rgt - self.model_class.lft == 1)

    def get_tree(self):
        return self.order_by(self.model_class.tree_id, self.model_class.lft)
