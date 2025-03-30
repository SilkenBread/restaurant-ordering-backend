from typing import Optional
from django.core.cache import cache
from django.db import models
from apps.core.repositories.django_repository import DjangoRepository
from apps.users.models import User


class UserRepository(DjangoRepository[User]):
    def __init__(self):
        super().__init__(User)
        self.cache_timeout = 60 * 5  # 5 minutos

    def get_by_email(self, email: str) -> Optional[User]:
        cache_key = f'user_email_{email}'
        user = cache.get(cache_key)
        
        if not user:
            user = self.model_class.objects.filter(email=email).first()
            if user:
                cache.set(cache_key, user, self.cache_timeout)
        
        return user
