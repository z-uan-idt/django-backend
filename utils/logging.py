import logging

from constants import AppMode


COLOR_CMD = {
    "BLACK": "\033[30m",
    "RED": "\033[31m",
    "GREEN": "\033[32m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "MAGENTA": "\033[35m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "DEFAULT": "\033[39m",
}


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": COLOR_CMD["DEFAULT"],
        "INFO": COLOR_CMD["CYAN"],
        "WARNING": COLOR_CMD["YELLOW"],
        "ERROR": COLOR_CMD["RED"],
        "RESET": "\033[0m",
    }

    def format(self, record):
        client_ip = ""
        if hasattr(record, "client_ip"):
            client_ip = f"{record.client_ip} - "

        message = client_ip + super().format(record)

        if record.levelname in self.COLORS:
            output = f"{self.COLORS[record.levelname]}Pharmago    │ {message}{self.COLORS['RESET']}"
            if (
                hasattr(record, "simplified_traceback")
                and not AppMode.DEBUG
                and record.simplified_traceback
            ):
                output = output.replace(f"{record.simplified_traceback}", "")
                output = output.replace(":\n", "")
            return output

        return message


class VietnameseFormatter(logging.Formatter):
    def __init__(
        self, fmt=None, datefmt=None, style="%", validate=True, ensure_ascii=False
    ):
        super().__init__(fmt, datefmt, style, validate)
        self.ensure_ascii = ensure_ascii

    def format(self, record):
        client_ip = ""
        if hasattr(record, "client_ip"):
            client_ip = f"{record.client_ip} - "

        return client_ip + super().format(record)


class FilterLogging(logging.Filter):
    def filter(self, record):
        if record.msg is None:
            if hasattr(record, "request"):
                request = record.request
                record.msg = f'"{record.method} {request.get_full_path()} {record.http_version}" {record.status_code}'

        return super().filter(record)


class ProductionFilterLogging(logging.Filter):
    def filter(self, record):
        return not AppMode.DEBUG


class DebugFilterLogging(logging.Filter):
    def filter(self, record):
        return AppMode.DEBUG
