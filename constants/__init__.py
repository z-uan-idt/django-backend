from decouple import config, Choices


class AppMode:
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"
    DEVELOPMENT = "development"

    choices = [TEST, STAGING, PRODUCTION, DEVELOPMENT]

    current = config("ENV", default=DEVELOPMENT, cast=Choices(choices, cast=str))

    DEBUG = current != PRODUCTION
