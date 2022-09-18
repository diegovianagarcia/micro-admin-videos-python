from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional
from __seedwork.domain.entities import Entity
from __seedwork.domain.exceptions import EntityValidationException
from category.domain.validators import CategoryValidatorFactory


@dataclass(kw_only=True, frozen=True, slots=True)
class Category(Entity):
    name: str
    description: Optional[str] = None
    is_active:  Optional[bool] = True
    created_at: Optional[datetime] = field(
        default_factory=datetime.now)

    def __post_init__(self):
        if not self.created_at:
            self._set('created_at', datetime.now())
        self.validate()

    def update(self, name: str, description: str):
        self._set("name", name)
        self._set("description", description)
        self.validate()

    def activate(self):
        self._set("is_active", True)

    def deactivate(self):
        self._set("is_active", False)

    # @classmethod
    # def validate(cls, name: str, description: str, is_active: bool = None):
    #     # domain expert defined max_lenght=255
    #     ValidatorRules(name, 'name').required().string().max_length(255)
    #     ValidatorRules(description, 'description').string()
    #     ValidatorRules(is_active, 'is_active').boolean()
    def validate(self):
        validator = CategoryValidatorFactory.create()
        is_valid = validator.validate(self.to_dict())
        if not is_valid:
            raise EntityValidationException(validator.errors)
