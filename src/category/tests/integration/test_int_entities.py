# pylint: disable=unexpected-keyword-arg
import unittest
from __seedwork.domain.exceptions import EntityValidationException
from category.domain.entities import Category


class TestCategoryIntegration(unittest.TestCase):

    def test_invalid_cases_for_name_prop(self):
        invalid_data = [
            {
                'data': {'name': None},
                'expected': 'This field may not be null.'},
            {
                'data': {'name': ''},
                'expected': 'This field may not be blank.'},
            {
                'data': {'name': 5},
                'expected': 'Not a valid string.'},
            {
                'data': {'name': 't'*256},
                'expected': 'Ensure this field has no more than 255 characters.'
            }
        ]

        for item in invalid_data:
            with self.assertRaises(EntityValidationException, msg=item['expected']) as assert_error:
                Category(**item['data'])
            self.assertIn('name', assert_error.exception.error)
            self.assertListEqual(
                assert_error.exception.error['name'],
                [item['expected']],
                f'Expected {item["expected"]}, actual {assert_error.exception.error["name"][0]}'
            )

    def test_invalid_cases_for_description_prop(self):
        with self.assertRaises(EntityValidationException) as assert_error:
            Category(name='Movie', description=5)
        self.assertEqual(
            assert_error.exception.error['description'], ['Not a valid string.'])

    def test_invalid_cases_for_is_active(self):
        with self.assertRaises(EntityValidationException) as assert_error:
            Category(name='Movie', is_active=5)
        self.assertEqual(
            assert_error.exception.error['is_active'], ['Must be a valid boolean.'])

    def test_valid_cases(self):
        try:
            Category(name='Movie')
            Category(name='Movie', description='')
            Category(name='Movie', is_active=True)
            Category(name='Movie',
                     description='some description',
                     is_active=False)
        except EntityValidationException as exception:
            self.fail(f'Some prop is not valid. Error {exception.error}')

    def test_update_with_invalid_cases_for_name_prop(self):
        invalid_data = [
            {
                'data': {'name': None},
                'expected': 'This field may not be null.'
            },
            {
                'data': {'name': ''},
                'expected': 'This field may not be blank.'
            },
            {
                'data': {'name': 5},
                'expected': 'Not a valid string.'
            },
            {
                'data': {'name': 't'*256},
                'expected': 'Ensure this field has no more than 255 characters.'
            }
        ]
        category = Category(name='Movie')
        for item in invalid_data:
            with self.assertRaises(EntityValidationException, msg=item['expected']) as assert_error:
                category.update(item['data']['name'], None)
            self.assertIn('name', assert_error.exception.error)
            self.assertListEqual(
                assert_error.exception.error['name'],
                [item['expected']],
                f'Expected {item["expected"]}, actual {assert_error.exception.error["name"][0]}'
            )

    def test_update_with_invalid_cases_for_description_prop(self):
        category = Category(name='Movie')
        with self.assertRaises(EntityValidationException) as assert_error:
            category.update('Movie', 5)
        self.assertEqual(
            assert_error.exception.error['description'], ['Not a valid string.'])

    def test_update_with_valid_cases(self):
        category = Category(name='Movie')
        try:
            category.update('Movie', '')
            category.update('Movie', 'some description')
        except EntityValidationException as exception:
            self.fail(f'Some prop is not valid. Error {exception.error}')

    # def test_invalid_cases_for_name_prop(self):
    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name=None)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name is required')

    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name='')
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name is required')

    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name=5)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name must be a string')

    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name='t'*256)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name must be less than 255 characters')

    # def test_invalid_cases_for_description_prop(self):
    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name='Movie', description=5)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The description must be a string')

    # def test_invalid_cases_for_is_active(self):
    #     with self.assertRaises(ValidationException) as assert_error:
    #         Category(name='Movie', is_active=5)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The is_active must be a boolean')

    # def test_valid_cases(self):
    #     try:
    #         Category(name='Movie')
    #         Category(name='Movie', description='')
    #         Category(name='Movie', is_active=True)
    #         Category(name='Movie',
    #                  description='some description',
    #                  is_active=False)
    #     except ValidationException as exception:
    #         self.fail(f'Some prop is not valid. Error {exception.args[0]}')

    # def test_update_with_invalid_cases_for_name_prop(self):
    #     category = Category(name='Movie')
    #     with self.assertRaises(ValidationException) as assert_error:
    #         category.update(None, None)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name is required')

    #     with self.assertRaises(ValidationException) as assert_error:
    #         category.update(5, None)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name must be a string')

    #     with self.assertRaises(ValidationException) as assert_error:
    #         category.update('t'*256, None)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The name must be less than 255 characters')

    # def test_update_with_invalid_cases_for_description_prop(self):
    #     category = Category(name='Movie')
    #     with self.assertRaises(ValidationException) as assert_error:
    #         category.update('Movie', 5)
    #     self.assertEqual(
    #         assert_error.exception.args[0], 'The description must be a string')

    # def test_update_with_valid_cases(self):
    #     category = Category(name='Movie')
    #     try:
    #         category.update('Movie', '')
    #         category.update('Movie', 'some description')
    #     except ValidationException as exception:
    #         self.fail(f'Some prop is not valid. Error {exception.args[0]}')
