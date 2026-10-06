from math import ceil
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class Page[T](ApiModel):
    items: list[T]
    pagination: Pagination


def page_meta(page: int, page_size: int, total: int) -> Pagination:
    return Pagination(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )


class TagIn(ApiModel):
    key: str = Field(min_length=1, max_length=128)
    value: str = Field(max_length=256)
