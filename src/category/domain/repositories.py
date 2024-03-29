from abc import ABC
from __seedwork.domain.repositories import (
    SearchableRepositoryInterface,
    SearchParams as DefaultSearchParams,
    SearchResult as DefaultSearchResult
)

from category.domain.entities import Category


class _SearchParams(DefaultSearchParams):  # pylint: disable=too-few-public-methods
    pass


class _SearchResult(DefaultSearchResult):  # pylint: disable=too-few-public-methods
    pass


class CategoryRepository(
        SearchableRepositoryInterface[Category, _SearchParams, _SearchResult], ABC):
    # simulate a inner class
    SearchParams = _SearchParams
    SearchResult = _SearchResult
