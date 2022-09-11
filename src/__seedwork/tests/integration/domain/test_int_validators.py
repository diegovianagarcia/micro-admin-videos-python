import unittest
from rest_framework import serializers
from __seedwork.domain.validators import DRFValidator, StrictBooleanField, StrictCharField


# pylint: disable=abstract-method
class StubSerialize(serializers.Serializer):
    name = serializers.CharField()
    price = serializers.IntegerField()


class TestDRFValidatorIntegration(unittest.TestCase):

    def test_validation_with_error(self):
        validator = DRFValidator(None, None)
        serializer = StubSerialize(data={})
        is_valid = validator.validate(serializer)
        self.assertFalse(is_valid)
        self.assertEqual(
            validator.errors,
            {
                'name': ['This field is required.'],
                'price': ['This field is required.']
            }
        )

    def test_validation_without_error(self):
        validator = DRFValidator(None, None)
        serializer = StubSerialize(data={'name': 'some value', 'price': 5})
        is_valid = validator.validate(serializer)
        self.assertTrue(is_valid)
        self.assertEqual(
            validator.validate_data,
            {
                'name': 'some value',
                'price': 5
            }
        )


class TestStrictCharFieldInt(unittest.TestCase):

    def test_if_is_invalid_when_not_str_value(self):
        class StubStrictCharFieldSerializer(serializers.Serializer):
            name = StrictCharField()

        serializer = StubStrictCharFieldSerializer(data={'name': 5})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'name': [serializers.ErrorDetail(string='Not a valid string.', code='invalid')]
        })

        serializer = StubStrictCharFieldSerializer(data={'name': True})
        serializer.is_valid()
        self.assertEqual(serializer.errors, {
            'name': [serializers.ErrorDetail(string='Not a valid string.', code='invalid')]
        })

    def test_none_value_is_valid(self):
        class StubStrictCharFieldSerializer(serializers.Serializer):
            name = StrictCharField(allow_null=True, required=False)

        serializer = StubStrictCharFieldSerializer(data={'name': None})
        self.assertTrue(serializer.is_valid())

    def test_str_value_is_valid(self):
        class StubStrictCharFieldSerializer(serializers.Serializer):
            name = StrictCharField(allow_null=True, required=False)

        serializer = StubStrictCharFieldSerializer(data={'name': 'some value'})
        self.assertTrue(serializer.is_valid())


class TestStrictBooleanFieldInt(unittest.TestCase):

    def test_if_is_invalid_when_not_boolean_value(self):
        class StubStrictBooleanFieldSerializer(serializers.Serializer):
            active = StrictBooleanField()

        invalid_values = [0, 1, "True", "False"]
        for value in invalid_values:
            serializer = StubStrictBooleanFieldSerializer(
                data={'active': value})
            serializer.is_valid()
            self.assertEqual(serializer.errors, {
                'active': [
                    serializers.ErrorDetail(
                        string='Must be a valid boolean.',
                        code='invalid'
                    )
                ]
            }, msg=f'when value: {value}')

    def test_is_valid(self):
        class StubStrictBooleanFieldSerializer(serializers.Serializer):
            active = StrictBooleanField(allow_null=True)

        serializer = StubStrictBooleanFieldSerializer(data={'active': None})
        self.assertTrue(serializer.is_valid())

        serializer = StubStrictBooleanFieldSerializer(data={'active': True})
        self.assertTrue(serializer.is_valid())

        serializer = StubStrictBooleanFieldSerializer(data={'active': False})
        self.assertTrue(serializer.is_valid())
