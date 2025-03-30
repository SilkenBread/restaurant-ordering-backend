from dataclasses import dataclass

@dataclass
class TokenDTO:
    """
    DTO para tokens JWT
    
    Attributes:
        access (str): Token de acceso
        refresh (str): Token de refresco
    """
    access: str
    refresh: str
