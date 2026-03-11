class RepositoryError(Exception):
    """Raised when a repository (database) operation fails."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause


class ServiceError(Exception):
    """Raised when a service operation fails (e.g. due to RepositoryError)."""

    def __init__(self, message: str, *, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.cause = cause
