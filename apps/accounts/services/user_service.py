from utils.base_service import BaseService
from utils.decorators import singleton

from ..models.user import User


@singleton
class UserService(BaseService[User]):
    
    def __init__(self):
        self.model = User
        super().__init__()
    
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)