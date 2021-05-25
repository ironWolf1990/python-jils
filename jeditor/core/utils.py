import uuid


def UniqueIdentifier() -> str:
    return uuid.uuid4().hex