from dataclasses import dataclass


@dataclass(frozen=True)
class Outgoing:
    text: object
    model: object
    mode: object
    model_present: bool
    mode_present: bool
    tell: bool
    choice_id: object
    has_choice: bool

    @staticmethod
    def from_payload(payload: object) -> "Outgoing":
        body = payload if isinstance(payload, dict) else {}
        return Outgoing(
            text=body.get("text"),
            model=body.get("model"),
            mode=body.get("mode"),
            model_present="model" in body,
            mode_present="mode" in body,
            tell=body.get("tell") is True,
            choice_id=body.get("choice_id"),
            has_choice="choice_id" in body,
        )
