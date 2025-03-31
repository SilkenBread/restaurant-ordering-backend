from apps.users.repositories.user_repository import UserRepository
from apps.users.services.user_service import UserService

repository = UserRepository()
service = UserService(repository=repository)

def get_user_service():
    return service
