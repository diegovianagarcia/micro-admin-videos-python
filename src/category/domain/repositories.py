from abc import ABC
from __seedwork.domain.repositories import RepositoryInterface
from category.domain.entities import Category


class CategoryRepository(RepositoryInterface[Category], ABC):
    pass
