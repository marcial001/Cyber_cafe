class AppError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Ressource introuvable"):
        super().__init__(message, "NOT_FOUND")


class ConflictError(AppError):
    def __init__(self, message: str = "Conflit d'état"):
        super().__init__(message, "CONFLICT")


class ValidationError(AppError):
    def __init__(self, message: str = "Données invalides"):
        super().__init__(message, "VALIDATION")
