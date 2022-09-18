# pylint: disable=unexpected-keyword-arg

from dataclasses import asdict, dataclass
from typing import Optional
from __seedwork.application.dto import PaginationOutput, PaginationOutputMapper, SearchInput
from __seedwork.application.use_cases import UseCase
from category.domain.entities import Category
from category.application.dto import CategoryOutput, CategoryOutputMapper
from category.domain.repositories import CategoryRepository


@dataclass(slots=True, frozen=True)
class CreateCategoryUseCase(UseCase):
    category_repo: CategoryRepository

    @dataclass(slots=True, frozen=True)
    class Input:  # DTO
        name: str
        description: Optional[str] = Category.get_field('description').default
        is_active: Optional[bool] = Category.get_field('is_active').default

    @dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass

    def execute(self, input_param: Input) -> Output:
        category = Category(
            name=input_param.name,
            description=input_param.description,
            is_active=input_param.is_active
        )
        self.category_repo.insert(category)
        return CategoryOutputMapper.\
            from_child(CreateCategoryUseCase.Output).\
            to_output(category)


@dataclass(slots=True, frozen=True)
class GetCategoryUseCase(UseCase):
    category_repo: CategoryRepository

    @dataclass(slots=True, frozen=True)
    class Input:  # DTO
        # pylint: disable=invalid-name
        id: str

    @dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass

    def execute(self, input_param: Input) -> Output:
        category = self.category_repo.find_by_id(input_param.id)
        return CategoryOutputMapper.\
            from_child(GetCategoryUseCase.Output).\
            to_output(category)


@dataclass(slots=True, frozen=True)
class ListCategoryUseCase(UseCase):
    category_repo: CategoryRepository

    @dataclass(slots=True, frozen=True)
    class Input(SearchInput[str]):
        pass

    @dataclass(slots=True, frozen=True)
    class Output(PaginationOutput):
        pass

    def execute(self, input_param: Input) -> Output:
        search_params = self.category_repo.SearchParams(**asdict(input_param))
        result = self.category_repo.search(search_params)
        return self.__to_output(result)

    def __to_output(self, result: CategoryRepository.SearchResult) -> Output:
        items = list(
            map(CategoryOutputMapper.without_child().to_output, result.items)
        )
        return PaginationOutputMapper.\
            from_child(ListCategoryUseCase.Output).\
            to_output(items, result)


@dataclass(slots=True, frozen=True)
class UpdateCategoryUseCase(UseCase):  # pylint: disable=too-few-public-methods
    category_repo: CategoryRepository

    @dataclass(slots=True, frozen=True)
    class Input:
        # pylint: disable=invalid-name
        id: str
        name: str
        description: Optional[str] = Category.get_field('description').default
        is_active: Optional[bool] = Category.get_field('is_active').default

    @dataclass(slots=True, frozen=True)
    class Output(CategoryOutput):
        pass

    def execute(self, input_param: Input) -> Output:
        category = self.category_repo.find_by_id(input_param.id)
        category.update(input_param.name, input_param.description)
        if input_param.is_active is True:
            category.activate()
        else:
            category.deactivate()
        self.category_repo.update(category)
        return self.__to_output(category)

    def __to_output(self, category: Category) -> Output:
        return CategoryOutputMapper.\
            from_child(self.Output).\
            to_output(category)


@dataclass(slots=True, frozen=True)
class DeleteCategoryUseCase(UseCase):
    category_repo: CategoryRepository

    @dataclass(slots=True, frozen=True)
    class Input:  # DTO
        # pylint: disable=invalid-name
        id: str

    def execute(self, input_param: Input) -> None:
        self.category_repo.delete(input_param.id)
