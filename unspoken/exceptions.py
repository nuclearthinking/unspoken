class UnspokenException(Exception):
    """Base class for all exceptions raised by Unspoken."""


class EncodingError(UnspokenException):
    """Raised when an encoding error occurs."""


class TranscriptNotFound(UnspokenException):
    """Raised when a transcript cannot be found."""


class TempFileNotFoundError(UnspokenException):
    """Raised when a temporary file cannot be found."""


class TaskNotFoundError(UnspokenException):
    """Raised when a task cannot be found."""
