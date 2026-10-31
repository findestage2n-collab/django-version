from core.kernel.errors import ConflictError, ValidationFailed


class WeakPasswordError(ValidationFailed):
    code = "weak_password"
    default_message = "Mot de passe refusé par la politique de sécurité."

    def __init__(self, problems: list[str]):
        super().__init__({"password": problems})


class UsernameTakenError(ConflictError):
    code = "username_taken"
    default_message = "Cet identifiant est déjà utilisé."
