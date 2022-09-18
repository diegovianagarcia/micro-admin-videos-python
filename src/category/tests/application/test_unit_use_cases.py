# pylint: disable=no-value-for-parameter, unexpected-keyword-arg
from datetime import datetime, timedelta
from typing import Optional
import unittest
from unittest.mock import patch
from __seedwork.application.dto import PaginationOutput, SearchInput

from __seedwork.application.use_cases import UseCase
from __seedwork.domain.exceptions import NotFoundExeption
from category.application.use_cases import (
    CreateCategoryUseCase,
    DeleteCategoryUseCase,
    GetCategoryUseCase,
    ListCategoryUseCase,
    UpdateCategoryUseCase
)
from category.domain.entities import Category
from category.domain.repositories import CategoryRepository
from category.infra.repositories import CategoryInMemoryRepository
from category.application.dto import CategoryOutput, CategoryOutputMapper


class TestCreateCategoryUseCaseUnit(unittest.TestCase):
    use_case: CreateCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = CreateCategoryUseCase(category_repo=self.category_repo)

    def test_if_instance_use_case(self):
        self.assertIsInstance(self.use_case, UseCase)

    def test_input(self):
        self.assertEqual(self.use_case.Input.__annotations__, {
            'name': str,
            'description': Optional[str],
            'is_active': Optional[bool]
        })

        # pylint: disable=no-member
        description_field = self.use_case.Input.__dataclass_fields__[
            'description']
        self.assertEqual(description_field.default,
                         Category.get_field('description').default)

        is_active_field = self.use_case.Input.__dataclass_fields__[
            'is_active']
        self.assertEqual(is_active_field.default,
                         Category.get_field('is_active').default)

    def test_output(self):
        self.assertTrue(issubclass(
            CreateCategoryUseCase.Output, CategoryOutput))

    def test_execute(self):
        with patch.object(self.category_repo, 'insert',
                          wraps=self.category_repo.insert) as spy_insert:
            input_params = CreateCategoryUseCase.Input(name='Movie')
            output = self.use_case.execute(input_params)
            spy_insert.assert_called_once()
            self.assertEqual(output, CreateCategoryUseCase.Output(
                id=self.category_repo.items[0].id,
                name='Movie',
                description=None,
                is_active=True,
                created_at=self.category_repo.items[0].created_at
            ))

        input_params = CreateCategoryUseCase.Input(
            name='Movie', description='Some description', is_active=False)
        output = self.use_case.execute(input_params)
        self.assertEqual(output, CreateCategoryUseCase.Output(
            id=self.category_repo.items[1].id,
            name='Movie',
            description='Some description',
            is_active=False,
            created_at=self.category_repo.items[1].created_at
        ))

        input_params = CreateCategoryUseCase.Input(
            name='Movie', description='Some description', is_active=True)
        output = self.use_case.execute(input_params)
        self.assertEqual(output, CreateCategoryUseCase.Output(
            id=self.category_repo.items[2].id,
            name='Movie',
            description='Some description',
            is_active=True,
            created_at=self.category_repo.items[2].created_at
        ))


class TestGetCategoryUseCaseUnit(unittest.TestCase):
    use_case: GetCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = GetCategoryUseCase(category_repo=self.category_repo)

    def test_if_instance_use_case(self):
        self.assertIsInstance(self.use_case, UseCase)

    def test_input(self):
        self.assertEqual(self.use_case.Input.__annotations__, {
            'id': str,
        })

    def test_output(self):
        self.assertTrue(issubclass(
            GetCategoryUseCase.Output, CategoryOutput))

    def test_raise_exception_when_catagory_not_found(self):
        input_params = GetCategoryUseCase.Input(id='fake id')
        with self.assertRaises(NotFoundExeption) as assert_error:
            self.use_case.execute(input_params)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'fake id'")

    def test_execute(self):
        category = Category(name="Movie")
        self.category_repo.items = [category]
        with patch.object(self.category_repo, 'find_by_id',
                          wraps=self.category_repo.find_by_id) as spy_find_by_id:
            input_params = GetCategoryUseCase.Input(id=category.id)
            output = self.use_case.execute(input_params)
            spy_find_by_id.assert_called_once()
            expected = GetCategoryUseCase.Output(
                id=category.id,
                name='Movie',
                description=None,
                is_active=True,
                created_at=category.created_at
            )
            self.assertEqual(output, expected)


class TestListCategoryUseCaseUnit(unittest.TestCase):
    use_case: ListCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = ListCategoryUseCase(category_repo=self.category_repo)

    def test_if_instance_use_case(self):
        self.assertIsInstance(self.use_case, UseCase)

    def test_input(self):
        self.assertTrue(issubclass(
            ListCategoryUseCase.Input, SearchInput))

    def test_output(self):
        self.assertTrue(issubclass(
            ListCategoryUseCase.Output, PaginationOutput))

    def test__to_output(self):
        category = Category(name='Movie')
        default_props = {
            "total": 1,
            "current_page": 1,
            "per_page": 2,
            "sort": None,
            "sort_dir": None,
            "filter": None
        }

        result = CategoryRepository.SearchResult(items=[], **default_props)
        output = self.use_case._ListCategoryUseCase__to_output(  # pylint: disable=protected-access
            result)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=[],
            total=1,
            current_page=1,
            last_page=1,
            per_page=2
        ))

        result = CategoryRepository.SearchResult(
            items=[category], **default_props)
        output = self.use_case._ListCategoryUseCase__to_output(  # pylint: disable=protected-access
            result)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=[CategoryOutputMapper.without_child().to_output(category)],
            total=1,
            current_page=1,
            last_page=1,
            per_page=2
        ))

    def test_execute_using_empty_search_params(self):
        self.category_repo.items = [
            Category(name='Test 1'),
            Category(name='Test 2', created_at=datetime.now() +
                     timedelta(seconds=200))
        ]
        with patch.object(self.category_repo, 'search',
                          wraps=self.category_repo.search) as spy_search:
            input_param = ListCategoryUseCase.Input()
            output = self.use_case.execute(input_param)
            spy_search.assert_called_once()
            expected = ListCategoryUseCase.Output(
                items=list(
                    map(CategoryOutputMapper.without_child().to_output,
                        self.category_repo.items[::-1])
                ),
                total=2,
                current_page=1,
                per_page=15,
                last_page=1
            )
            self.assertEqual(output, expected)

    def test_execute_using_paginate_and_sort_and_filter(self):
        items = [
            Category(name='a'),
            Category(name='AAA'),
            Category(name='AaA'),
            Category(name='b'),
        ]
        self.category_repo.items = items

        input_param = ListCategoryUseCase.Input(
            page=1, per_page=2, sort='name', sort_dir='asc', filter='a')
        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=list(
                map(CategoryOutputMapper.without_child(
                ).to_output, [items[1], items[2]])
            ),
            total=3,
            current_page=1,
            per_page=2,
            last_page=2
        ))

        input_param = ListCategoryUseCase.Input(
            page=2, per_page=2, sort='name', sort_dir='asc', filter='a')
        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=list(
                map(CategoryOutputMapper.without_child().to_output, [items[0]])
            ),
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        ))

        input_param = ListCategoryUseCase.Input(
            page=1, per_page=2, sort='name', sort_dir='desc', filter='a')
        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=list(
                map(CategoryOutputMapper.without_child(
                ).to_output, [items[0], items[2]])
            ),
            total=3,
            current_page=1,
            per_page=2,
            last_page=2
        ))

        input_param = ListCategoryUseCase.Input(
            page=2, per_page=2, sort='name', sort_dir='desc', filter='a')
        output = self.use_case.execute(input_param)
        self.assertEqual(output, ListCategoryUseCase.Output(
            items=list(
                map(CategoryOutputMapper.without_child().to_output, [items[1]])
            ),
            total=3,
            current_page=2,
            per_page=2,
            last_page=2
        ))


class TestUpdateCategoryUseCaseUnit(unittest.TestCase):
    use_case: UpdateCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = UpdateCategoryUseCase(category_repo=self.category_repo)

    def test_if_instance_use_case(self):
        self.assertIsInstance(self.use_case, UseCase)

    def test_input(self):
        self.assertEqual(self.use_case.Input.__annotations__, {
            'id': str,
            'name': str,
            'description': Optional[str],
            'is_active': Optional[bool]
        })

        # pylint: disable=no-member
        description_field = self.use_case.Input.__dataclass_fields__[
            'description']
        self.assertEqual(description_field.default,
                         Category.get_field('description').default)

        is_active_field = self.use_case.Input.__dataclass_fields__[
            'is_active']
        self.assertEqual(is_active_field.default,
                         Category.get_field('is_active').default)

    def test_output(self):
        self.assertTrue(issubclass(
            UpdateCategoryUseCase.Output, CategoryOutput))

    def test_raise_exception_when_category_not_found(self):
        id_not_found = '0f42ac99-08b0-4fef-923d-9187b3762a0d'
        input_params = UpdateCategoryUseCase.Input(
            id=id_not_found, name='Movie')
        with self.assertRaises(NotFoundExeption) as assert_error:
            self.use_case.execute(input_params)
        self.assertEqual(
            assert_error.exception.args[0], f"Entity not found using ID '{id_not_found}'")

    def test_execute(self):
        category = Category(name="Movie")
        self.category_repo.items = [category]
        with patch.object(self.category_repo, 'update',
                          wraps=self.category_repo.update) as spy_update:
            input_params = UpdateCategoryUseCase.Input(
                id=category.id,
                name='Name updated'
            )
            output = self.use_case.execute(input_params)
            spy_update.assert_called_once()
            self.assertEqual(output, UpdateCategoryUseCase.Output(
                id=category.id,
                name='Name updated',
                description=category.description,
                is_active=category.is_active,
                created_at=self.category_repo.items[0].created_at
            ))
        arrange = [
            {
                'input': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                },
                'expected': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                    'is_active': True,
                    'created_at': category.created_at
                }
            },
            {
                'input': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                    'is_active': False,
                },
                'expected': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                    'is_active': False,
                    'created_at': category.created_at
                }
            },
            {
                'input': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                    'is_active': True,
                },
                'expected': {
                    'id': category.id,
                    'name': 'Test name',
                    'description': 'Test description',
                    'is_active': True,
                    'created_at': category.created_at
                }
            },
            {
                'input': {
                    'id': category.id,
                    'name': 'Name updated',
                    'description': 'description updated',
                    'is_active': False,
                },
                'expected': {
                    'id': category.id,
                    'name': 'Name updated',
                    'description': 'description updated',
                    'is_active': False,
                    'created_at': category.created_at
                }
            }
        ]

        for item in arrange:
            input_params = UpdateCategoryUseCase.Input(**item['input'])
            output = self.use_case.execute(input_params)
            self.assertEqual(
                output, UpdateCategoryUseCase.Output(**item['expected']),
                msg=f'Test input: {item["input"]}')


class TestDeleteCategoryUseCaseUnit(unittest.TestCase):
    use_case: DeleteCategoryUseCase
    category_repo: CategoryInMemoryRepository

    def setUp(self) -> None:
        self.category_repo = CategoryInMemoryRepository()
        self.use_case = DeleteCategoryUseCase(category_repo=self.category_repo)

    def test_if_instance_use_case(self):
        self.assertIsInstance(self.use_case, UseCase)

    def test_input(self):
        self.assertEqual(self.use_case.Input.__annotations__, {
            'id': str,
        })

    def test_raise_exception_when_catagory_not_found(self):
        input_params = DeleteCategoryUseCase.Input(id='fake id')
        with self.assertRaises(NotFoundExeption) as assert_error:
            self.use_case.execute(input_params)
        self.assertEqual(
            assert_error.exception.args[0], "Entity not found using ID 'fake id'")

    def test_execute(self):
        category = Category(name="Movie")
        self.category_repo.items = [category]
        with patch.object(self.category_repo, 'delete',
                          wraps=self.category_repo.delete) as spy_delete:
            input_params = DeleteCategoryUseCase.Input(id=category.id)
            self.use_case.execute(input_params)
            spy_delete.assert_called_once()
            self.assertEqual(self.category_repo.items, [])
