from dataclasses import dataclass
from typing import Optional

@dataclass
class UserResponseDTO:
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    access: str
    refresh: str
