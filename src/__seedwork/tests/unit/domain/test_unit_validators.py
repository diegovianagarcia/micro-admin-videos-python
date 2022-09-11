from dataclasses import fields
import unittest
from unittest.mock import MagicMock, PropertyMock, patch
from __seedwork.domain.exceptions import ValidationException
from __seedwork.domain.validators import DRFValidator, ValidatorFieldsInterface, ValidatorRules
from rest_framework.serializers import Serializer


class TestValidatorRulesUnit(unittest.TestCase):

    def test_values_method(self):
        validator = ValidatorRules.values('some value', 'prop')
        self.assertIsInstance(validator, ValidatorRules)
        self.assertEqual(validator.value, 'some value')
        self.assertEqual(validator.prop, 'prop')

    def test_required_rule(self):
        self.assertIsInstance(ValidatorRules.values(
            'some value', 'prop'), ValidatorRules)
        invalid_data = [
            {'value': None, 'prop': 'prop'},
            {'value': '', 'prop': 'prop'},
        ]
        for item in invalid_data:
            msg = f'value: {item["value"]}, prop: {item["prop"]}'
            with self.assertRaises(ValidationException, msg=msg) as assert_error:
                ValidatorRules.values(item['value'], item['prop']).required()
            self.assertEqual(
                'The prop is required',
                assert_error.exception.args[0]
            )

        valid_data = [
            {'value': 'test', 'prop': 'prop'},
            {'value': '5', 'prop': 'prop'},
            {'value': '0', 'prop': 'prop'},
            {'value': 'False', 'prop': 'prop'},
        ]
        for item in valid_data:
            self.assertIsInstance(
                ValidatorRules.values(item['value'], item['prop']).required(),
                ValidatorRules
            )

    def test_string_rule(self):
        self.assertIsInstance(ValidatorRules.values(
            'some value', 'prop').string(), ValidatorRules)

        self.assertIsInstance(ValidatorRules.values(
            None, 'prop').string(), ValidatorRules)

        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(1, 'prop').string()
        self.assertEqual(
            'The prop must be a string',
            assert_error.exception.args[0]
        )

    def test_string_max_length_rule(self):
        self.assertIsInstance(ValidatorRules.values(
            't'*4, 'prop').max_length(4), ValidatorRules)

        self.assertIsInstance(ValidatorRules.values(
            None, 'prop').max_length(1), ValidatorRules)

        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values('t'*5, 'prop').max_length(4)
        self.assertEqual(
            'The prop must be less than 4 characters',
            assert_error.exception.args[0]
        )

    def test_boolean_rule(self):
        invalid_data = [
            (1, 'prop'),
            ("test", 'prop'),
        ]
        for item in invalid_data:
            with self.assertRaises(ValidationException) as assert_error:
                ValidatorRules.values(*item).boolean()
                self.assertEqual(
                    'The prop must be a boolean',
                    assert_error.exception.args[0]
                )
        valid_data = [
            (None, 'prop'),
            (True, 'prop'),
            (False, 'prop'),

        ]
        for item in valid_data:
            self.assertIsInstance(ValidatorRules.values(*item), ValidatorRules)

    def test_throw_a_validation_exception_when_combine_two_or_more_reules(self):
        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(
                None,
                'prop'
            ).required().string().max_length(5)
        self.assertEqual(
            'The prop is required',
            assert_error.exception.args[0]
        )

        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(
                5,
                'prop'
            ).required().string().max_length(5)
        self.assertEqual(
            'The prop must be a string',
            assert_error.exception.args[0]
        )

        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(
                't' * 6,
                'prop'
            ).required().string().max_length(5)
        self.assertEqual(
            'The prop must be less than 5 characters',
            assert_error.exception.args[0]
        )

        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(
                None,
                'prop'
            ).required().boolean()
        self.assertEqual(
            'The prop is required',
            assert_error.exception.args[0]
        )
        with self.assertRaises(ValidationException) as assert_error:
            ValidatorRules.values(
                5,
                'prop'
            ).required().boolean()
        self.assertEqual(
            'The prop must be a boolean',
            assert_error.exception.args[0]
        )

    def test_valid_cases_for_combination_rules(self):
        ValidatorRules.values('test', 'prop').required().string()
        ValidatorRules.values('t'*5, 'prop').required().string().max_length(5)

        ValidatorRules.values(True, 'prop').required().boolean()
        ValidatorRules.values(False, 'prop').required().boolean()
        # pylint: disable=redundant-unittest-assert
        self.assertTrue(True)


class TestValidatorFieldsInterfaceUnit(unittest.TestCase):

    def test_throw_error_when_validated_method_not_implemented(self):
        with self.assertRaises(TypeError) as assert_error:
            # pylint: disable=abstract-class-instantiated, no-value-for-parameter
            ValidatorFieldsInterface()
        self.assertEqual(
            assert_error.exception.args[0],
            "Can't instantiate abstract class ValidatorFieldsInterface"
            " with abstract method validate")

    def test_contract(self):
        fields_class = fields(ValidatorFieldsInterface)

        errors_field = fields_class[0]
        self.assertEqual(errors_field.name, 'errors')
        self.assertEqual(errors_field.default, None)

        errors_field = fields_class[1]
        self.assertEqual(errors_field.name, 'validate_data')
        self.assertEqual(errors_field.default, None)


class TestDRFValidatorUnit(unittest.TestCase):

    @patch.object(Serializer, 'is_valid', return_value=True)
    @patch.object(Serializer, 'validated_data', return_value={'field': 'value'},
                  new_callable=PropertyMock)
    def test_if_validated_data_is_set(self,
                                      mock_validated_data: PropertyMock,
                                      mock_is_valid: MagicMock):
        validator = DRFValidator(None, None)
        is_valid = validator.validate(Serializer())
        self.assertTrue(is_valid)
        self.assertEqual(validator.validate_data,
                         mock_validated_data.return_value)
        mock_is_valid.assert_called()

    @patch.object(Serializer, 'is_valid', return_value=False)
    @patch.object(Serializer, 'errors', return_value={'field': ['some error']},
                  new_callable=PropertyMock)
    def test_if_errors_is_set(self,
                              mock_validated_data: PropertyMock,
                              mock_is_valid: MagicMock):
        validator = DRFValidator(None, None)
        is_valid = validator.validate(Serializer())
        self.assertFalse(is_valid)
        self.assertEqual(validator.errors,
                         mock_validated_data.return_value)
        mock_is_valid.assert_called()
