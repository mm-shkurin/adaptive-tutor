from domain.chat.choice import Choice
from domain.chat.source import Source


def draft_choices(sources: tuple[Source, ...]) -> tuple[tuple[Choice, ...], str]:
    choices = []
    for index in range(4):
        if index < len(sources):
            text = sources[index].text
        else:
            text = f"option-{index + 1}"
        choices.append(Choice(f"c{index + 1}", text))
    return tuple(choices), "c1"
