class ZenHttpException(Exception):
    """Exception with HTTP status code."""

    def __init__(self, status):
        """Creates an instance.

        Args:
            status (int): HTTP status code.
        """

        self.status = status

