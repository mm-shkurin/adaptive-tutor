from dataclasses import dataclass


@dataclass(frozen=True)
class Choice:
    id: str
    text: str

    def json(self) -> dict:
        return {"id": self.id, "text": self.text}
