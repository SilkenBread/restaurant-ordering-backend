# restaurants/dtos/restaurant_dto.py
from dataclasses import dataclass
from django.utils.translation import gettext_lazy as _

@dataclass
class RestaurantDTO:
    name: str
    address: str
    rating: float
    status: str
    category: str
    latitude: float
    longitude: float
    is_active: bool = True
    
    def validate(self):
        errors = {}
        if not self.name:
            errors['name'] = _('Name is required')
        if self.rating < 0 or self.rating > 5:
            errors['rating'] = _('Rating must be between 0 and 5')
        return errors
