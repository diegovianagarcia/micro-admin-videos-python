# pylint: disable=unexpected-keyword-arg, protected-access
from datetime import datetime, timedelta
import unittest
from category.domain.entities import Category

from category.infra.repositories import CategoryInMemoryRepository


class TestCategoryInMemoryRepositoryUnit(unittest.TestCase):
    repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.repo = CategoryInMemoryRepository()

    def test_if_no_filter_when_filter_para_is_none(self):
        items = [Category(name='Movie')]

        items_filtered = self.repo._apply_filter(items, None)
        self.assertEqual(items_filtered, items)

    def test_filter(self):
        items = [
            Category(name='Movie New'),
            Category(name='movie old'),
            Category(name='Some'),
        ]

        items_filtered = self.repo._apply_filter(items, 'MOVIE')
        self.assertEqual(items_filtered, [items[0], items[1]])

    def test_sort_by_created_at_when_sort_is_none(self):
        now = datetime.now()
        items = [
            Category(name='Movie', created_at=now + timedelta(minutes=1)),
            Category(name='movie', created_at=now + timedelta(minutes=10)),
        ]

        items_sorted = self.repo._apply_sort(items, None, None)
        self.assertEqual(items_sorted, [items[1], items[0]])

    def test_sort(self):
        items = [
            Category(name='b'),
            Category(name='a'),
            Category(name='c'),
        ]

        items_sorted = self.repo._apply_sort(items, 'name', 'asc')
        self.assertEqual(items_sorted, [items[1], items[0], items[2]])

        items_sorted = self.repo._apply_sort(items, 'name', 'desc')
        self.assertEqual(items_sorted, [items[2], items[0], items[1]])
