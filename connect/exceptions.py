
class TooManyRequests(Exception):
    def __init__(self, message=None) -> None:
        super().__init__(message)

class Unauthorized(Exception):
    def __init__(self, message=None) -> None:
        super().__init__(message)
