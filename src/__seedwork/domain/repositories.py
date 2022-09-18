from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import math
from typing import Any, Generic, List, TypeVar, Optional

from __seedwork.domain.entities import Entity, UniqueEntityId
from __seedwork.domain.exceptions import NotFoundExeption

ET = TypeVar('ET', bound=Entity)


class RepositoryInterface(Generic[ET], ABC):

    @abstractmethod
    def insert(self, entity: ET) -> None:
        raise NotImplementedError()

    @abstractmethod
    def find_by_id(self, entity_id: str | UniqueEntityId) -> ET:
        raise NotImplementedError()

    @abstractmethod
    def find_all(self) -> List[ET]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, entity: ET) -> None:
        raise NotImplementedError()

    @abstractmethod
    def delete(self, entity_id: str | UniqueEntityId) -> None:
        raise NotImplementedError()


Input = TypeVar('Input')
Output = TypeVar('Output')


class SearchableRepositoryInterface(Generic[ET, Input, Output], RepositoryInterface[ET], ABC):
    sortable_fields: List[str] = []

    @abstractmethod
    def search(self, input_params: Input) -> Output:
        raise NotImplementedError()


Filter = TypeVar('Filter', str, Any)


@dataclass(slots=True, kw_only=True)
class SearchParams:
    page: Optional[int] = 1
    per_page: Optional[int] = 15
    sort: Optional[str] = None
    sort_dir: Optional[str] = None
    filter: Optional[Filter] = None

    def __post_init__(self):
        self._normalize_page()
        self._normalize_per_page()
        self._normalize_sort()
        self._normalize_sort_dir()
        self._normalize_filter()

    def _normalize_page(self):
        page = self._convert_to_int(self.page)
        if page <= 0:
            page = self._get_dataclass_field('page').default
        self.page = page

    def _normalize_per_page(self):
        per_page = self._convert_to_int(self.per_page)
        if per_page <= 0:
            per_page = self._get_dataclass_field('per_page').default
        self.per_page = per_page

    def _normalize_sort(self):
        self.sort = None if self.sort == '' or self.sort is None \
            else str(self.sort)

    def _normalize_sort_dir(self):
        if not self.sort:
            self.sort_dir = None
            return
        sort_dir = str(self.sort_dir).lower()
        self.sort_dir = 'asc' if sort_dir not in ('asc', 'desc') else sort_dir

    def _normalize_filter(self):
        self.filter = None if self.filter == '' or self.filter is None \
            else str(self.filter)

    def _convert_to_int(self, value: Any, default=0) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def _get_dataclass_field(self, field_name):
        # pylint: disable=no-member
        return SearchParams.__dataclass_fields__[field_name]


@dataclass(slots=True, kw_only=True, frozen=True)
class SearchResult(Generic[ET, Filter]):  # pylint: disable=too-many-instance-attributes
    items: List[ET]
    total: int
    current_page: int
    per_page: int
    last_page: int = field(init=False)
    sort: Optional[str] = None
    sort_dir: Optional[str] = None
    filter: Optional[Filter] = None

    def __post_init__(self):
        object.__setattr__(self, 'last_page',
                           math.ceil(self.total / self.per_page))

    def to_dict(self):
        return {
            'items': self.items,
            'total': self.total,
            'current_page': self.current_page,
            'per_page': self.per_page,
            'last_page': self.last_page,
            'sort': self.sort,
            'sort_dir': self.sort_dir,
            'filter': self.filter
        }


@dataclass(slots=True)
class InMemoryRepository(RepositoryInterface[ET], ABC):
    items: List[ET] = field(default_factory=lambda: [])

    def insert(self, entity: ET) -> None:
        self.items.append(entity)

    def find_by_id(self, entity_id: str | UniqueEntityId) -> ET:
        return self._get(str(entity_id))

    def find_all(self) -> List[ET]:
        return self.items

    def update(self, entity: ET) -> None:
        entity_found = self._get(entity.id)
        index = self.items.index(entity_found)
        self.items[index] = entity

    def delete(self, entity_id: str | UniqueEntityId) -> None:
        entity_found = self._get(str(entity_id))
        self.items.remove(entity_found)

    def _get(self, entity_id: str) -> ET:
        if entity := next(filter(lambda item: item.id == entity_id, self.items), None):
            return entity
        raise NotFoundExeption(f"Entity not found using ID '{entity_id}'")


class InMemorySearchRepository(
    InMemoryRepository[ET],
    SearchableRepositoryInterface[
        ET,
        SearchParams,
        SearchResult[ET, Filter],
    ],
    ABC
):
    def search(self, input_params: SearchParams) -> SearchResult[ET, Filter]:
        items_filtered = self._apply_filter(self.items, input_params.filter)
        items_sorted = self._apply_sort(
            items_filtered, input_params.sort, input_params.sort_dir)
        items_paginated = self._apply_paginate(
            items_sorted, input_params.page, input_params.per_page)

        return SearchResult(
            items=items_paginated,
            total=len(items_filtered),
            current_page=input_params.page,
            per_page=input_params.per_page,
            sort=input_params.sort,
            sort_dir=input_params.sort_dir,
            filter=input_params.filter
        )

    @abstractmethod
    def _apply_filter(self, items: List[ET], filter_param: Optional[Filter]) -> List[ET]:
        raise NotImplementedError()

    def _apply_sort(self, items: List[ET],
                    sort: Optional[str], sort_dir: Optional[str]) -> List[ET]:
        if sort and sort in self.sortable_fields:
            is_reverse = sort_dir == 'desc'
            return sorted(items, key=lambda item: getattr(item, sort), reverse=is_reverse)
        return items

    def _apply_paginate(self, items: List[ET], page: int, per_page: int) -> List[ET]:
        start = (page-1) * per_page
        limit = start + per_page
        return items[slice(start, limit)]
