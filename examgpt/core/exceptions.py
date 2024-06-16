class BaseException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class PromptNotFound(BaseException):
    """Raised when prompt for a scenario is not found"""

    def __init__(self, message: str = "Prompt not found"):
        super().__init__(message=message)


class NotEnoughInformationInContext(BaseException):
    """Raised when provided text chunk does not have enough information to create a question"""

    def __init__(
        self,
        chunk_id: str,
    ):
        message: str = f"Text chunk does not have enough information to create a question: {chunk_id}"
        super().__init__(message=message)


# TODO: Remove
class UndefinedCheckpointPath(BaseException):
    """Raised when trying to checkpoint some data without defining checkpoint file first"""

    def __init__(self):
        message = "Undefined checkpoint file. Call the CheckpointService() first to set the checkpoint file"
        super().__init__(message=message)
