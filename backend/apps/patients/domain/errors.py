from core.kernel.errors import ConflictError, ValidationFailed


class InvalidPatientData(ValidationFailed):
    pass


class DuplicatePatientError(ConflictError):
    code = "duplicate_patient"
    default_message = "Un patient de même nom, prénom et date de naissance existe déjà."
