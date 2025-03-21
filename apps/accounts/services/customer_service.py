from utils.base_service import BaseService
from utils.decorators import singleton

from ..models.customer import Customer


@singleton
class CustomerService(BaseService[Customer]):
    
    @classmethod
    def get_model(cls):
        return Customer
    
    def __init__(self):
        self.model = Customer
        super().__init__()