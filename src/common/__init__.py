class BrokenInvariantError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)
