"""Domain error types.

These carry a machine-readable ``code`` and a human ``detail`` but know nothing about HTTP.
The API layer maps each type to a status code.
"""


class DomainError(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


class NotFoundError(DomainError):
    """The requested resource does not exist."""


class RuleViolationError(DomainError):
    """A game rule refused the requested move."""


class ConcurrentWriteError(DomainError):
    """Another write landed first, so this one was based on stale state."""
