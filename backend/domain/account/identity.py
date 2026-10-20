from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderIdentity:
    subject: str
    email: str
    name: str
