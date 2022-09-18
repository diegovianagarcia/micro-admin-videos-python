from typing import List, Optional
from __seedwork.domain.repositories import InMemorySearchRepository
from category.domain.entities import Category
from category.domain.repositories import CategoryRepository


class CategoryInMemoryRepository(
    CategoryRepository,
    InMemorySearchRepository[Category, str]
):
    sortable_fields: List[str] = ['name', 'created_at']

    def _apply_filter(self,
                      items: List[Category], filter_param: Optional[str]) -> List[Category]:
        if filter_param:
            return list(filter(lambda i: filter_param.lower() in i.name.lower(), items))
        return items

    def _apply_sort(self, items: List[Category],
                    sort: Optional[str], sort_dir: Optional[str]) -> List[Category]:
        if sort:
            return super()._apply_sort(items, sort, sort_dir)
        return super()._apply_sort(items, 'created_at', 'desc')
