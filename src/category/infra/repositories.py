from typing import List, Optional
from __seedwork.domain.repositories import (
    Filter,
    InMemorySearchRepository,
    SearchParams as DefaultSearchParams,
    SearchResult as DefaultSearchResult
)
from category.domain.entities import Category
from category.domain.repositories import CategoryRepository


class _SearchParams(DefaultSearchParams):
    pass


class _SearchResult(DefaultSearchResult):
    pass


class CategoryInMemoryRepository(
    CategoryRepository,
    InMemorySearchRepository[Category, str]
):
    # simulate a inner class
    SearchParams = _SearchParams
    SearchResult = _SearchResult
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
        else:
            return super()._apply_sort(items, 'created_at', 'desc')
