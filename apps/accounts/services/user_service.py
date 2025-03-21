from utils.base_service import BaseService
from utils.decorators import singleton

from ..models.user import User


@singleton
class UserService(BaseService[User]):
    
    def __init__(self):
        self.model = User
        super().__init__()