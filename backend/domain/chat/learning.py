from dataclasses import dataclass

LISTED_MODELS = frozenset(
    {
        "auto",
        "auto:smart",
        "auto:fast",
        "qwen/qwen3-32b",
        "meta-llama/llama-3.3-70b",
        "google/gemini-2.0-flash",
        "mistralai/mistral-small",
        "deepseek/deepseek-chat",
        "fusion",
    }
)
LISTED_MODES = frozenset({"professor", "five_year_old", "socratic", "examiner"})
GROUNDED_MODES = frozenset({"professor", "five_year_old"})


class EmptyQuestion(Exception):
    """A send needs a question that is not blank."""


class ModelNotListed(Exception):
    """The model is null or not one of the listed ids."""


class ModeNotListed(Exception):
    """The mode is null or not one of the listed modes."""


@dataclass(frozen=True)
class Question:
    text: str

    @staticmethod
    def parse(text: object) -> "Question":
        if not isinstance(text, str) or text.strip() == "":
            raise EmptyQuestion()
        return Question(text)


@dataclass(frozen=True)
class ListedModel:
    value: str

    @staticmethod
    def parse(value: object, present: bool) -> "ListedModel":
        if not present:
            return ListedModel("auto")
        if not isinstance(value, str) or value not in LISTED_MODELS:
            raise ModelNotListed()
        return ListedModel(value)


@dataclass(frozen=True)
class LearningMode:
    value: str

    @staticmethod
    def parse(value: object, present: bool) -> "LearningMode":
        if not present:
            return LearningMode("professor")
        if not isinstance(value, str) or value not in LISTED_MODES:
            raise ModeNotListed()
        return LearningMode(value)

    def require_grounded(self) -> "LearningMode":
        if self.value not in GROUNDED_MODES:
            raise ModeNotListed()
        return self
