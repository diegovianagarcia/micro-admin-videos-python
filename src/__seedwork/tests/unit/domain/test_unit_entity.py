# pylint: disable=unexpected-keyword-arg

from abc import ABC
from dataclasses import dataclass, is_dataclass
import unittest

from __seedwork.domain.entities import Entity
from __seedwork.domain.value_objects import UniqueEntityId


@dataclass(frozen=True, kw_only=True, slots=True)
class StubEntity(Entity):
    prop1: str
    prop2: str


class TestEntityUnit(unittest.TestCase):

    def test_is_is_a_dataclass(self):
        self.assertTrue(is_dataclass(Entity))

    def test_is_is_a_abstract_class(self):
        self.assertIsInstance(Entity(), ABC)

    def test_id_and_props(self):
        entity = StubEntity(prop1='value1', prop2='value2')
        self.assertEqual(entity.prop1, 'value1')
        self.assertEqual(entity.prop2, 'value2')
        self.assertIsInstance(entity.unique_entity_id, UniqueEntityId)
        self.assertEqual(entity.unique_entity_id.id, entity.id)

    def test_accept_a_valid_uuid(self):
        entity = StubEntity(
            unique_entity_id=UniqueEntityId(
                '0f42ac99-08b0-4fef-923d-9187b3762a0d'),
            prop1='value1',
            prop2='value2'
        )
        self.assertEqual(entity.id, '0f42ac99-08b0-4fef-923d-9187b3762a0d')

    def test_to_dict_method(self):
        entity = StubEntity(
            unique_entity_id=UniqueEntityId(
                '0f42ac99-08b0-4fef-923d-9187b3762a0d'),
            prop1='value1',
            prop2='value2'
        )
        self.assertDictEqual(entity.to_dict(), {
            'id': '0f42ac99-08b0-4fef-923d-9187b3762a0d',
            'prop1': 'value1',
            'prop2': 'value2'
        })

    def test_set_method(self):
        entity = StubEntity(prop1='value1', prop2='value2')
        # pylint: disable=protected-access
        entity._set("prop1", "changed prop1")
        self.assertEqual(entity.prop1, "changed prop1")
