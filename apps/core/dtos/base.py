from dataclasses import dataclass
from typing import List, Generic, TypeVar

T = TypeVar('T')

@dataclass
class ListDTO(Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
