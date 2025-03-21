from django.utils.translation import gettext_lazy as _


class ErrorType:
    REQUIRED = "required"
    BLANK = "blank"
    NULL = "null"
    INVALID = "invalid"
    UNIQUE = "unique"

    MAX_LENGTH = "max_length"
    MIN_LENGTH = "min_length"

    MAX_VALUE = "max_value"
    MIN_VALUE = "min_value"

    INVALID_CHOICE = "invalid_choice"


class ErrorMessages:
    
    @staticmethod
    def CharField(verbose_name: str, max_length=None):
        verbose_name = verbose_name.capitalize()
        
        return {
            ErrorType.REQUIRED: f"{verbose_name} không được bỏ trống",
            ErrorType.BLANK: f"{verbose_name} không được bỏ trống",
            ErrorType.NULL: f"{verbose_name} không được bỏ trống",
            ErrorType.MAX_LENGTH: f'{verbose_name} không thể dài hơn {max_length} ký tự',
            ErrorType.INVALID: f'{verbose_name} không hợp lệ',
            ErrorType.UNIQUE: f'{verbose_name} đã tồn tại trên hệ thống',
        }

    @staticmethod
    def ChoicesField(verbose_name: str):
        verbose_name = verbose_name.capitalize()

        return {
            ErrorType.REQUIRED: f"{verbose_name} không được bỏ trống",
            ErrorType.BLANK: f"{verbose_name} không được bỏ trống",
            ErrorType.NULL: f"{verbose_name} không được bỏ trống",
            ErrorType.INVALID: f'{verbose_name} không hợp lệ',
        }

    @staticmethod
    def IntegerField(verbose_name: str, min_value=None, max_value=None):
        verbose_name = verbose_name.capitalize()

        return {
            ErrorType.REQUIRED: f"{verbose_name} không được bỏ trống",
            ErrorType.INVALID: f'{verbose_name} không hợp lệ',
            ErrorType.MAX_VALUE: f"{verbose_name} không thể lớn hơn {max_value}",
            ErrorType.MIN_VALUE: f"{verbose_name} không thể nhỏ hơn {min_value}",
            ErrorType.NULL: f"{verbose_name} không được bỏ trống",
        }

    @staticmethod
    def DateField(verbose_name: str):
        verbose_name = verbose_name.capitalize()

        return {
            ErrorType.REQUIRED: f"{verbose_name} không được bỏ trống",
            ErrorType.INVALID: f'{verbose_name} không hợp lệ',
            ErrorType.NULL: f"{verbose_name} không được bỏ trống",
        }

    @staticmethod
    def FileField(verbose_name: str, limit_value=None):
        verbose_name = verbose_name.capitalize()

        return {
            ErrorType.REQUIRED: f"{verbose_name} không được bỏ trống",
            ErrorType.INVALID: f'{verbose_name} không hợp lệ',
            ErrorType.NULL: f"{verbose_name} không được bỏ trống",
        }