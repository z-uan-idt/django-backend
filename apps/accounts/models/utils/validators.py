from django.core.exceptions import ValidationError

import re

from constants.error_messages import ErrorMessages, ErrorType


def validate_phone_number(value):

    deleted_pattern = r'^.+__deleted__\d+$'
    if re.match(deleted_pattern, value):
        return
    
    phone_pattern = r'^0\d{9,10}$'
    
    if not re.match(phone_pattern, value):
        raise ValidationError(ErrorMessages.CharField('Số điện thoại')[ErrorType.INVALID])