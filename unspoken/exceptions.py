class UnspokenException(Exception):
    """Base class for all exceptions raised by Unspoken."""


class EncodingError(UnspokenException):
    """Raised when an encoding error occurs."""


class TranscriptNotFound(UnspokenException):
    """Raised when a transcript cannot be found."""
