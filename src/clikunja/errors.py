class CLIError(Exception):
    exit_code = 1


class ConfigError(CLIError):
    exit_code = 4


class AuthError(CLIError):
    exit_code = 2


class APIError(CLIError):
    exit_code = 3

    def __init__(self, status: int, body: str, message: str | None = None):
        self.status = status
        self.body = body
        super().__init__(message or f"API error {status}: {body}")
