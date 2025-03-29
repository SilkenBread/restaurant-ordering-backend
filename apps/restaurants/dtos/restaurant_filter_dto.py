from dataclasses import dataclass
from typing import Optional

@dataclass
class RestaurantFilterDTO:
    name: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    
    def validate(self):
        errors = {}
        if self.min_rating is not None and (self.min_rating < 0 or self.min_rating > 5):
            errors['min_rating'] = 'Rating must be between 0 and 5'
        if self.max_rating is not None and (self.max_rating < 0 or self.max_rating > 5):
            errors['max_rating'] = 'Rating must be between 0 and 5'
        return errors
