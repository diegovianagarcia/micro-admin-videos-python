from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from __seedwork.domain.validators import ErrorFields


class InvalidUuidException(Exception):
    def __init__(self, error='ID must be a valid UUID') -> None:  # pylint: disable=useless-super-delegation
        super().__init__(error)


class ValidationException(Exception):
    pass


class EntityValidationException(Exception):
    error: 'ErrorFields'

    def __init__(self, error: 'ErrorFields') -> None:
        self.error = error
        super().__init__('Entity Validation Error')


class NotFoundExeption(Exception):
    pass
