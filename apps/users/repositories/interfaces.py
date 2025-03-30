from abc import ABC, abstractmethod
from typing import Optional, List
from ..models import User

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def create(self, user_data: dict) -> User:
        pass
    
    @abstractmethod
    def update(self, user: User, user_data: dict) -> User:
        pass
    
    @abstractmethod
    def delete(self, user: User) -> None:
        pass
    
    @abstractmethod
    def filter(self, filters: dict) -> List[User]:
        pass
