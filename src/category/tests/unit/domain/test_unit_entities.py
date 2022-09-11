# pylint: disable=unexpected-keyword-arg
from dataclasses import FrozenInstanceError, is_dataclass
from datetime import datetime
import unittest
from unittest import mock
from unittest.mock import patch
from category.domain.entities import Category

# TDD - Kent Beck


class TestCategoryUnit(unittest.TestCase):

    def test_if_is_a_dataclass(self):
        self.assertTrue(is_dataclass(Category))

    def test_constructor(self):
        with patch.object(Category, 'validate') as mock_validate_method:
            category = Category(name="Movie")
            mock_validate_method.assert_called_once()
            self.assertEqual(category.name, "Movie")
            self.assertEqual(category.description, None)
            self.assertEqual(category.is_active, True)
            self.assertIsInstance(category.created_at, datetime)

        created_at = datetime.now()
        category = Category(
            name="Movie",
            description="some description",
            is_active=False,
            created_at=created_at
        )
        self.assertEqual(category.name, "Movie")
        self.assertEqual(category.description, "some description")
        self.assertEqual(category.is_active, False)
        self.assertEqual(category.created_at, created_at)

    def test_if_created_at_is_generated_in_constructor(self):
        with patch.object(Category, 'validate'):
            category1 = Category(name="Movie1")
            category2 = Category(name="Movie2")
            self.assertNotEqual(category1.created_at, category2.created_at)

    def test_is_immutable(self):
        with patch.object(Category, 'validate'):
            with self.assertRaises(FrozenInstanceError):
                value_object = Category(name='teste')
                value_object.name = 'fake id'

    def test_update(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movieeeee")
            category.update("Movie", "Movie description")
            self.assertEqual(category.name, "Movie")
            self.assertEqual(category.description, "Movie description")

    def test_activate(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movie", is_active=False)
            category.activate()
            self.assertEqual(category.is_active, True)

    def test_deactivate(self):
        with patch.object(Category, 'validate'):
            category = Category(name="Movie", is_active=True)
            category.deactivate()
            self.assertEqual(category.is_active, False)
