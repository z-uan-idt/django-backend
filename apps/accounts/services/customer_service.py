from utils.base_service import BaseService
from utils.decorators import singleton

from ..models.customer import Customer


@singleton
class CustomerService(BaseService[Customer]):
    
    def __init__(self):
        self.model = Customer
        super().__init__()
    
    def get_queryset(self):
        return super().get_queryset().filter(is_delete=False)